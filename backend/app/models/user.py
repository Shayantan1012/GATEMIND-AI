from dataclasses import dataclass, field
from typing import List

from app.models.enums import AccountStatus, Branch
from app.models.session import Session
from app.models.user_profile import UserProfile


@dataclass
class User:
    user_id: str
    full_name: str
    email: str
    password_hash: str
    mobile_number: str
    branch: Branch
    target_gate_year: int
    is_email_verified: bool = False
    account_status: AccountStatus = AccountStatus.PENDING_VERIFICATION
    user_profile: UserProfile | None = None
    sessions: List[Session] = field(default_factory=list)

    def activate(self) -> None:
        self.is_email_verified = True
        self.account_status = AccountStatus.ACTIVE
