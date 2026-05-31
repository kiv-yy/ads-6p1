from uuid import UUID

from sqlalchemy import or_

from app.models import Claim, ClaimStatus, Item
from app.repositories.base import BaseRepository


class ClaimRepository(BaseRepository):
    def create(self, claim: Claim) -> Claim:
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

    def has_accepted_for_item(self, item_id: UUID) -> bool:
        return self.db.query(Claim).filter(Claim.item_id == item_id, Claim.status == ClaimStatus.ACCEPTED.value).first() is not None
