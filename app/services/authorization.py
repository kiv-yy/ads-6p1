from app.models import Claim, ClaimStatus, Item, User, UserRole


class AuthorizationPolicy:
    @staticmethod
    def can_manage_item(item: Item, user: User) -> bool:
        return item.owner_id == user.id or user.role == UserRole.ADMIN.value

    @staticmethod
    def can_access_claim(claim: Claim, user: User) -> bool:
        return claim.claimant_id == user.id or claim.item.owner_id == user.id or user.role == UserRole.ADMIN.value

    @staticmethod
    def can_moderate_claim(claim: Claim, user: User) -> bool:
        return claim.item.owner_id == user.id or user.role == UserRole.ADMIN.value

    @staticmethod
    def can_chat(claim: Claim, user: User) -> bool:
        return AuthorizationPolicy.can_access_claim(claim, user) and claim.status == ClaimStatus.ACCEPTED.value
