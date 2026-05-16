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

    def to_dict(self) -> dict:
        return {
            "_id": self.user_id,
            "full_name": self.full_name,
            "email": self.email,
            "password_hash": self.password_hash,
            "mobile_number": self.mobile_number,
            "branch": self.branch.value,
            "target_gate_year": self.target_gate_year,
            "is_email_verified": self.is_email_verified,
            "account_status": self.account_status.value,
            "user_profile": self.user_profile.to_dict() if self.user_profile else None,
            "sessions": [session.to_dict() for session in self.sessions],
        }

    @staticmethod
    def from_dict(data: dict) -> "User":
        return User(
            user_id=str(data.get("_id") or data.get("user_id", "")),
            full_name=data.get("full_name", ""),
            email=data.get("email", ""),
            password_hash=data.get("password_hash", ""),
            mobile_number=data.get("mobile_number", ""),
            branch=Branch(data.get("branch", Branch.OTHER.value)),
            target_gate_year=int(data.get("target_gate_year", 0)),
            is_email_verified=data.get("is_email_verified", False),
            account_status=AccountStatus(data.get("account_status", AccountStatus.PENDING_VERIFICATION.value)),
            user_profile=UserProfile.from_dict(data.get("user_profile")) if data.get("user_profile") else None,
            sessions=[Session.from_dict(s) for s in data.get("sessions", [])],
        )

    def activate(self) -> None:
        self.is_email_verified = True
        self.account_status = AccountStatus.ACTIVE
