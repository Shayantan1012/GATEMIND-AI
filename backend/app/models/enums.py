from enum import Enum


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    BLOCKED = "BLOCKED"
    DEACTIVATED = "DEACTIVATED"
    OTHER = "OTHER"


class Branch(str, Enum):
    CSE = "CSE"
    ECE = "ECE"
    EE = "EE"
    ME = "ME"
    CE = "CE"
    OTHER = "OTHER"
