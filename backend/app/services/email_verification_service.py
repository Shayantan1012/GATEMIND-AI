import secrets
from datetime import datetime, timedelta, timezone


class VerificationStrategy:
    def send_verification(self, user) -> str:
        raise NotImplementedError

    def verify(self, token: str) -> bool:
        raise NotImplementedError


class EmailVerificationService(VerificationStrategy):
    def __init__(self, email_notification_service):
        self.email_notification_service = email_notification_service
        self._tokens = {}
        self._otps = {}

    def send_verification(self, user) -> str:
        token = self.generate_email_token(user)
        verification_link = f"https://your-app.example.com/verify-email?token={token}"
        self.email_notification_service.send_verification_email(user.email, verification_link)
        return token

    def verify(self, token: str) -> bool:
        return self.verify_email_token(token) is not None

    def generate_email_token(self, user) -> str:
        token = secrets.token_urlsafe(32)
        self._tokens[token] = {
            "user_id": user.user_id,
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=24),
        }
        return token

    def verify_email_token(self, token: str) -> str | None:
        token_data = self._tokens.get(token)
        if not token_data:
            return None
        if token_data["expires_at"] < datetime.now(timezone.utc):
            self._tokens.pop(token, None)
            return None
        self._tokens.pop(token, None)
        return token_data["user_id"]

    def send_otp(self, user) -> str:
        otp = f"{secrets.randbelow(1000000):06d}"
        self._otps[otp] = {
            "user_id": user.user_id,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
        }
        self.email_notification_service.send_otp_email(user.email, otp)
        return otp

    def verify_otp(self, otp: str) -> str | None:
        otp_data = self._otps.get(otp)
        if not otp_data:
            return None
        if otp_data["expires_at"] < datetime.now(timezone.utc):
            self._otps.pop(otp, None)
            return None
        self._otps.pop(otp, None)
        return otp_data["user_id"]
