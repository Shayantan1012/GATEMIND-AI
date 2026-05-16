from datetime import datetime, timedelta, timezone

import jwt


class JWTService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"

    def generate_access_token(self, user) -> str:
        return self._encode(user.user_id, "access", timedelta(minutes=30))

    def generate_refresh_token(self, user) -> str:
        return self._encode(user.user_id, "refresh", timedelta(days=7))

    def validate_token(self, token: str) -> dict:
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

    def extract_user_id(self, token: str) -> str:
        payload = self.validate_token(token)
        return payload["sub"]

    def refresh_token(self, refresh_token: str) -> str:
        payload = self.validate_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Only refresh tokens can generate new access tokens")
        fake_user = type("TokenUser", (), {"user_id": payload["sub"]})
        return self.generate_access_token(fake_user)

    def _encode(self, user_id: str, token_type: str, expires_delta: timedelta) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "type": token_type,
            "iat": now,
            "exp": now + expires_delta,
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
