import secrets
from datetime import datetime, timedelta, timezone


class OTPVerificationService:
    def __init__(self, sms_notification_service):
        self.sms_notification_service = sms_notification_service
        self._otps = {}

    def send_otp(self, user) -> str:
        otp = f"{secrets.randbelow(1000000):06d}"
        self._otps[otp] = {
            "user_id": user.user_id,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
        }
        sent = self.sms_notification_service.send_otp_sms(user.mobile_number, otp)
        if not sent:
            self._otps.pop(otp, None)
            raise ValueError("Unable to send OTP SMS")
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
