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


class AdminRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    CONTENT_ADMIN = "CONTENT_ADMIN"
    MOCKTEST_ADMIN = "MOCKTEST_ADMIN"
    ANALYTICS_ADMIN = "ANALYTICS_ADMIN"
    SUPPORT_ADMIN = "SUPPORT_ADMIN"


class QuestionType(str, Enum):
    MCQ = "MCQ"
    MSQ = "MSQ"
    NAT = "NAT"


class QueryType(str, Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    HYBRID = "HYBRID"
