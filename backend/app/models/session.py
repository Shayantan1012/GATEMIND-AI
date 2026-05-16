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

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expiry_time
