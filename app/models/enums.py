from enum import Enum


class ItemType(str, Enum):
    LOST = "kehilangan"
    FOUND = "temuan"


class ItemCategory(str, Enum):
    LOST = "Lost"
    FOUND = "Found"


class ItemStatus(str, Enum):
    OPEN = "aktif"
    IN_PROGRESS = "aktif"
    RESOLVED = "selesai"
    DELETED = "dihapus"


class ClaimStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "diterima"
    REJECTED = "ditolak"


class ReportStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "ditinjau"
    RESOLVED = "selesai"


class AdminActionType(str, Enum):
    WARNING = "warning"
    TAKEDOWN = "takedown"
    RESTORE = "restore"
    BAN_USER = "ban_user"
