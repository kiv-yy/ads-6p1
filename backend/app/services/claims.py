from uuid import UUID

from sqlalchemy.orm import Session

from app import schemas
from app.dependencies import ApiError
from app.models import ChatMessage, Claim, ClaimStatus, ItemStatus, User, UserRole
from app.repositories.chat import ChatRepository
from app.repositories.claims import ClaimRepository
from app.repositories.items import ItemRepository
from app.services.authorization import AuthorizationPolicy
from app.services.notifications import NotificationService


class ClaimService:
    def __init__(self, db: Session) -> None:
        self.claims = ClaimRepository(db)
        self.items = ItemRepository(db)
        self.chats = ChatRepository(db)
        self.notifications = NotificationService(db)

    def create(self, claim_in: schemas.ClaimCreate, claimant: User) -> Claim:
        item = self.items.get(claim_in.item_id)
        if not item:
            raise ApiError.not_found("Item")
        if item.owner_id == claimant.id:
            raise ApiError.bad_request("You cannot claim your own item")
        if item.status != ItemStatus.OPEN.value:
            raise ApiError.bad_request("Only active items can be claimed")
        if self.claims.get_active_for_item_and_claimant(item.id, claimant.id):
            raise ApiError.bad_request("You already have an active claim for this item")

        claim = Claim(
            item_id=claim_in.item_id,
            claimant_id=claimant.id,
            claimant_name=claim_in.claimant_name or claimant.full_name,
            message=claim_in.message or "",
            proof_image_url=str(claim_in.proof_image_url) if claim_in.proof_image_url else None,
            status=ClaimStatus.ACCEPTED.value,
        )
        saved_claim = self.claims.create(claim)
        saved_claim.item.status = ItemStatus.IN_PROGRESS.value
        self.claims.save(saved_claim.item)
        self.chats.get_or_create_for_claim(saved_claim)
        self.notifications.create(
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

    def get_for_participant(self, claim_id: UUID, current_user: User) -> Claim:
        claim = self.claims.get(claim_id)
        if not claim:
            raise ApiError.not_found("Claim")
        if not AuthorizationPolicy.can_access_claim(claim, current_user):
            raise ApiError.forbidden("Only claim participants can access this resource")
        return claim

    def list_for_item(self, item_id: UUID, current_user: User, skip: int = 0, limit: int = 50) -> list[Claim]:
        item = self.items.get(item_id)
        if not item:
            raise ApiError.not_found("Item")
        if not AuthorizationPolicy.can_manage_item(item, current_user):
            raise ApiError.forbidden("Only item owner can view item claims")
        return self.claims.list_for_item(item_id=item.id, skip=skip, limit=limit)

    def list_for_user(self, current_user: User, skip: int = 0, limit: int = 100) -> list[Claim]:
        claims = self.claims.list_all(skip=skip, limit=limit) if current_user.role == UserRole.ADMIN.value else self.claims.list_for_user(current_user.id)
        self._attach_latest_chat_metadata(claims)
        return claims

    def update_status(self, claim_id: UUID, claim_in: schemas.ClaimUpdate, current_user: User) -> Claim:
        claim = self.claims.get(claim_id)
        if not claim:
            raise ApiError.not_found("Claim")
        if not AuthorizationPolicy.can_moderate_claim(claim, current_user):
            raise ApiError.forbidden("Only item owner, admin, or the claimant can cancel claims")
        if current_user.id == claim.claimant_id and claim_in.status != ClaimStatus.REJECTED:
            raise ApiError.forbidden("Claimant can only cancel/reject their own claim")

        claim.status = claim_in.status.value
        if claim_in.status == ClaimStatus.ACCEPTED:
            claim.item.status = ItemStatus.IN_PROGRESS.value
            self.chats.get_or_create_for_claim(claim)
        elif claim_in.status == ClaimStatus.REJECTED and not self.claims.has_accepted_for_item(claim.item_id):
            claim.item.status = ItemStatus.OPEN.value
        saved_claim = self.claims.save(claim)
        title = "Klaim diterima" if claim_in.status == ClaimStatus.ACCEPTED else "Klaim ditolak"
        self.notifications.create(
            user_id=saved_claim.claimant_id,
            actor_id=saved_claim.item.owner_id,
            type="claim_status",
            title=title,
            message=f"{title} untuk {saved_claim.item.title}.",
            target_url=f"/messages/{saved_claim.id}" if claim_in.status == ClaimStatus.ACCEPTED else f"/items/{saved_claim.item_id}",
            item_id=saved_claim.item_id,
            claim_id=saved_claim.id,
        )
        return saved_claim

    def _attach_latest_chat_metadata(self, claims: list[Claim]) -> None:
        for claim in claims:
            chat = self.chats.get_for_claim(claim)
            latest_message: ChatMessage | None = self.chats.latest_message_for_chat(chat) if chat else None
            claim.latest_message_at = latest_message.created_at if latest_message else None
            if latest_message and latest_message.content:
                claim.latest_message_preview = latest_message.content
            elif latest_message and latest_message.image_attachment:
                claim.latest_message_preview = "Mengirim lampiran"
            else:
                claim.latest_message_preview = None
