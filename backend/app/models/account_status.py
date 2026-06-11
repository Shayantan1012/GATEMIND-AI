from enum import Enum


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    BLOCKED = "BLOCKED"
    DEACTIVATED = "DEACTIVATED"
    OTHER = "OTHER"
