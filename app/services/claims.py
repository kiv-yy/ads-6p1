from uuid import UUID

from sqlalchemy import or_

from app import schemas
from app.models import Claim, ClaimStatus, Item, ItemStatus, User
from app.services.base import BaseRepository
from app.services.chat import ChatRepository


class ClaimRepository(BaseRepository):
    def create(self, claim_in: schemas.ClaimCreate, claimant: User) -> Claim:
        claim = Claim(
            item_id=claim_in.item_id,
            claimant_id=claimant.id,
            claimant_name=claim_in.claimant_name or claimant.full_name,
            message=claim_in.message or "",
            proof_image_url=str(claim_in.proof_image_url) if claim_in.proof_image_url else None,
        )
        return self.save(claim)

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
        return self.save(claim)

    def _has_accepted_claim(self, item_id: UUID) -> bool:
        return self.db.query(Claim).filter(Claim.item_id == item_id, Claim.status == ClaimStatus.ACCEPTED.value).first() is not None
