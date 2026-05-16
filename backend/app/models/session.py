from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Session:
    session_id: str
    access_token: str
    refresh_token: str
    login_time: datetime
    expiry_time: datetime
    is_active: bool = True

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "login_time": self.login_time,
            "expiry_time": self.expiry_time,
            "is_active": self.is_active,
        }

    @staticmethod
    def from_dict(data: dict) -> "Session":
        if not data:
            return None
        return Session(
            session_id=data.get("session_id", ""),
            access_token=data.get("access_token", ""),
            refresh_token=data.get("refresh_token", ""),
            login_time=data.get("login_time"),
            expiry_time=data.get("expiry_time"),
            is_active=data.get("is_active", True),
        )

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expiry_time
