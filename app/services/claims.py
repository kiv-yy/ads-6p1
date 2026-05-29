from uuid import UUID

from sqlalchemy import or_

from app import schemas
from app.models import Claim, ClaimStatus, Item, ItemStatus, User
from app.services.base import BaseRepository
from app.services.chat import ChatRepository
from app.services.notifications import NotificationRepository


class ClaimRepository(BaseRepository):
    def create(self, claim_in: schemas.ClaimCreate, claimant: User) -> Claim:
        claim = Claim(
            item_id=claim_in.item_id,
            claimant_id=claimant.id,
            claimant_name=claim_in.claimant_name or claimant.full_name,
            message=claim_in.message or "",
            proof_image_url=str(claim_in.proof_image_url) if claim_in.proof_image_url else None,
            status=ClaimStatus.ACCEPTED.value,  # Set directly to accepted
        )
        saved_claim = self.save(claim)
        # Flag item status to in progress
        saved_claim.item.status = ItemStatus.IN_PROGRESS.value
        
        # Instantiate/get the Chat room session immediately
        ChatRepository(self.db).get_or_create_for_claim(saved_claim)

        # Send notification to item owner that someone has initiated contact and chat is open
        NotificationRepository(self.db).create(
            user_id=saved_claim.item.owner_id,
            actor_id=claimant.id,
            type="claim_status",
            title="Sesi chat baru",
            message=f"{claimant.full_name} memulai chat untuk {saved_claim.item.title}.",
            target_url=f"/messages/{saved_claim.id}",
            item_id=saved_claim.item_id,
            claim_id=saved_claim.id,
        )
        return saved_claim

    def get(self, claim_id: UUID) -> Claim | None:
        return self.db.get(Claim, claim_id)

    def get_active_for_item_and_claimant(self, item_id: UUID, claimant_id: UUID) -> Claim | None:
        return (
            self.db.query(Claim)
            .filter(
                Claim.item_id == item_id,
                Claim.claimant_id == claimant_id,
                Claim.status.in_([ClaimStatus.PENDING.value, ClaimStatus.ACCEPTED.value]),
            )
            .first()
        )

    def list_for_item(self, item_id: UUID, skip: int = 0, limit: int = 50) -> list[Claim]:
        return self.db.query(Claim).filter(Claim.item_id == item_id).order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()

    def list_for_user(self, user_id: UUID) -> list[Claim]:
        return (
            self.db.query(Claim)
            .join(Item)
            .filter(or_(Claim.claimant_id == user_id, Item.owner_id == user_id))
            .order_by(Claim.created_at.desc())
            .all()
        )

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Claim]:
        return self.db.query(Claim).order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()

    def update_status(self, claim: Claim, status: ClaimStatus) -> Claim:
        claim.status = status.value
        if status == ClaimStatus.ACCEPTED:
            claim.item.status = ItemStatus.IN_PROGRESS.value
            (
                self.db.query(Claim)
                .filter(Claim.item_id == claim.item_id, Claim.id != claim.id, Claim.status == ClaimStatus.PENDING.value)
                .update({Claim.status: ClaimStatus.REJECTED.value}, synchronize_session=False)
            )
            ChatRepository(self.db).get_or_create_for_claim(claim)
        elif status == ClaimStatus.REJECTED and not self._has_accepted_claim(claim.item_id):
            claim.item.status = ItemStatus.OPEN.value
        saved_claim = self.save(claim)
        title = "Klaim diterima" if status == ClaimStatus.ACCEPTED else "Klaim ditolak"
        target_url = f"/messages/{saved_claim.id}" if status == ClaimStatus.ACCEPTED else f"/items/{saved_claim.item_id}"
        NotificationRepository(self.db).create(
            user_id=saved_claim.claimant_id,
            actor_id=saved_claim.item.owner_id,
            type="claim_status",
            title=title,
            message=f"{title} untuk {saved_claim.item.title}.",
            target_url=target_url,
            item_id=saved_claim.item_id,
            claim_id=saved_claim.id,
        )
        return saved_claim

    def _has_accepted_claim(self, item_id: UUID) -> bool:
        return self.db.query(Claim).filter(Claim.item_id == item_id, Claim.status == ClaimStatus.ACCEPTED.value).first() is not None
