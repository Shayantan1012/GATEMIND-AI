import secrets
from datetime import datetime, timedelta, timezone

from app.services.verification.verification_strategy import VerificationStrategy


class EmailVerificationService(VerificationStrategy):
    def __init__(self, notification_service):
        self.notification_service = notification_service
        self._tokens = {}
        self._otps = {}

    def send_verification(self, user):
        token = self.generate_email_token(user)
        self.notification_service.send_verification_email(user.email, token)
        return token

    def verify(self, token):
        return self.verify_email_token(token)

    def generate_email_token(self, user):
        token = secrets.token_urlsafe(32)
        self._tokens[token] = {"user_id": user.user_id, "expires_at": datetime.now(timezone.utc) + timedelta(hours=24)}
        return token

    def verify_email_token(self, token):
        data = self._tokens.get(token)
        if not data or data["expires_at"] < datetime.now(timezone.utc):
            self._tokens.pop(token, None)
            return False
        self._tokens.pop(token, None)
        return True

    def send_otp(self, user):
        otp = f"{secrets.randbelow(1000000):06d}"
        self._otps[otp] = {"user_id": user.user_id, "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)}
        self.notification_service.send_otp_email(user.email, otp)
        return otp

    def verify_otp(self, otp):
        data = self._otps.get(otp)
        if not data or data["expires_at"] < datetime.now(timezone.utc):
            self._otps.pop(otp, None)
            return None
        self._otps.pop(otp, None)
        return data["user_id"]
