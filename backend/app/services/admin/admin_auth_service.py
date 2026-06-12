from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models.admin import Admin
from app.models.session import Session
from app.services.security.check_email import CheckEmail


class AdminAuthService:
    def __init__(self, repository, password_service, jwt_service, audit_logger):
        self.repository = repository
        self.password_service = password_service
        self.jwt_service = jwt_service
        self.audit_logger = audit_logger

    def register(self, data):
        missing = [key for key in ["full_name", "email", "password", "role"] if not data.get(key)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        if not CheckEmail.contains_necessary_character(data["email"]):
            raise ValueError("Invalid email address")
        if self.repository.exists_by_email(data["email"]):
            raise ValueError("Admin email already registered")
        if not self.password_service.validate_password_strength(data["password"]):
            raise ValueError("Password must be at least 8 characters and include letters and numbers")
        admin = Admin.create(data, self.password_service.hash_password(data["password"]))
        self.repository.save(admin)
        self.audit_logger.log(admin.admin_id, "ADMIN_REGISTERED", {"role": admin.role.value})
        return admin

    def login(self, email, password):
        admin = self.repository.find_by_email(email)
        if not admin or not self.password_service.verify_password(password, admin.password_hash):
            self.audit_logger.log(email, "ADMIN_LOGIN_FAILED")
            raise ValueError("Invalid email or password")
        if admin.account_status.value != "ACTIVE":
            self.audit_logger.log(admin.admin_id, "ADMIN_LOGIN_BLOCKED", {"status": admin.account_status.value})
            raise ValueError("Admin account is not active")
        access = self.jwt_service.generate_access_token(admin, "admin", admin.role.value)
        refresh = self.jwt_service.generate_refresh_token(admin, "admin", admin.role.value)
        admin.sessions.append(Session(str(uuid4()), access, refresh, datetime.now(timezone.utc), datetime.now(timezone.utc) + timedelta(days=7)))
        self.repository.update(admin)
        self.audit_logger.log(admin.admin_id, "ADMIN_LOGIN")
        return {"admin": admin, "access_token": access, "refresh_token": refresh}

    def logout(self, refresh_token):
        admin = self.repository.find_by_refresh_token(refresh_token)
        if not admin:
            return False
        for session in admin.sessions:
            if session.refresh_token == refresh_token:
                session.is_active = False
                self.repository.update(admin)
                self.audit_logger.log(admin.admin_id, "ADMIN_LOGOUT")
                return True
        return False
