from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from app.models.enums import AccountStatus, AdminRole
from app.models.session import Session


@dataclass
class Admin:
    admin_id: str
    full_name: str
    email: str
    password_hash: str
    phone_number: str
    role: AdminRole
    employee_id: str = ""
    job_title: str = ""
    department: str = ""
    is_verified: bool = True
    account_status: AccountStatus = AccountStatus.ACTIVE
    sessions: list[Session] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def user_id(self) -> str:
        return self.admin_id

    def to_dict(self) -> dict:
        return {
            "_id": self.admin_id,
            "full_name": self.full_name,
            "email": self.email,
            "password_hash": self.password_hash,
            "phone_number": self.phone_number,
            "role": self.role.value,
            "employee_id": self.employee_id,
            "job_title": self.job_title,
            "department": self.department,
            "is_verified": self.is_verified,
            "account_status": self.account_status.value,
            "sessions": [session.to_dict() for session in self.sessions],
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "Admin":
        return Admin(
            admin_id=str(data["_id"]),
            full_name=data["full_name"],
            email=data["email"],
            password_hash=data["password_hash"],
            phone_number=data.get("phone_number", ""),
            role=AdminRole(data.get("role", AdminRole.CONTENT_ADMIN.value)),
            employee_id=data.get("employee_id", ""),
            job_title=data.get("job_title", ""),
            department=data.get("department", ""),
            is_verified=data.get("is_verified", True),
            account_status=AccountStatus(data.get("account_status", AccountStatus.ACTIVE.value)),
            sessions=[Session.from_dict(item) for item in data.get("sessions", [])],
            created_at=data.get("created_at", datetime.now(timezone.utc)),
        )

    @staticmethod
    def create(data: dict, password_hash: str) -> "Admin":
        return Admin(
            admin_id=str(uuid4()),
            full_name=data["full_name"].strip(),
            email=data["email"].strip().lower(),
            password_hash=password_hash,
            phone_number=data.get("phone_number", "").strip(),
            role=AdminRole(data.get("role", AdminRole.CONTENT_ADMIN.value)),
            employee_id=data.get("employee_id", "").strip(),
            job_title=data.get("job_title", "").strip(),
            department=data.get("department", "").strip(),
        )
