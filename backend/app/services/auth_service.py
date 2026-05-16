from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models.enums import Branch
from app.models.session import Session
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services.check_email import CheckEmail


class AuthenticationService:
    def __init__(self, user_repository, password_service, jwt_service, verification_service):
        self.user_repository = user_repository
        self.password_service = password_service
        self.jwt_service = jwt_service
        self.verification_service = verification_service

    def register_user(self, data: dict) -> User:
        required_fields = [
            "full_name",
            "email",
            "password",
            "mobile_number",
            "branch",
            "target_gate_year",
        ]
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        email = data["email"].strip().lower()
        if not CheckEmail.contains_necessary_character(email):
            raise ValueError("Invalid email address")
        if self.user_repository.exists_by_email(email):
            raise ValueError("Email already registered")
        if not self.password_service.validate_password_strength(data["password"]):
            raise ValueError("Password must be at least 8 characters and include letters and numbers")

        branch = Branch(data["branch"]) if data["branch"] in Branch._value2member_map_ else Branch.OTHER
        user_id = str(uuid4())
        user = User(
            user_id=user_id,
            full_name=data["full_name"].strip(),
            email=email,
            password_hash=self.password_service.hash_password(data["password"]),
            mobile_number=data["mobile_number"].strip(),
            branch=branch,
            target_gate_year=int(data["target_gate_year"]),
            user_profile=UserProfile(profile_id=str(uuid4())),
        )
        self.user_repository.save(user)
        self.verification_service.send_otp(user)
        return user

    def authenticate_user(self, email: str, password: str) -> dict:
        user = self.user_repository.find_by_email(email)
        if not user or not self.password_service.verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")
        if user.account_status.value in {"BLOCKED", "DEACTIVATED"}:
            raise ValueError("Account is not active")

        access_token = self.jwt_service.generate_access_token(user)
        refresh_token = self.jwt_service.generate_refresh_token(user)
        user.sessions.append(
            Session(
                session_id=str(uuid4()),
                access_token=access_token,
                refresh_token=refresh_token,
                login_time=datetime.now(timezone.utc),
                expiry_time=datetime.now(timezone.utc) + timedelta(days=7),
            )
        )
        self.user_repository.update(user)
        return {"user": user, "access_token": access_token, "refresh_token": refresh_token}

    def logout_user(self, refresh_token: str) -> bool:
        for user in list(self.user_repository._users_by_id.values()):
            for session in user.sessions:
                if session.refresh_token == refresh_token:
                    session.is_active = False
                    self.user_repository.update(user)
                    return True
        return False

    def forgot_password(self, email: str) -> str:
        user = self.user_repository.find_by_email(email)
        if not user:
            return ""
        return self.verification_service.send_otp(user)

    def verify_email(self, token: str) -> bool:
        return self.verification_service.verify_email_token(token)

    def verify_otp(self, otp: str) -> User:
        user_id = self.verification_service.verify_otp(otp)
        if not user_id:
            raise ValueError("Invalid or expired OTP")
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        user.activate()
        self.user_repository.update(user)
        return user

    def refresh_token(self, refresh_token: str) -> str:
        return self.jwt_service.refresh_token(refresh_token)
