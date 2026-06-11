from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models.admin import Admin
from app.models.session import Session
from app.services.check_email import CheckEmail


class AuditLogger:
    def __init__(self, repository):
        self.repository = repository

    def log(self, actor_id: str, action: str, details: dict | None = None) -> None:
        self.repository.save(
            {
                "_id": str(uuid4()),
                "actor_id": actor_id,
                "action": action,
                "details": details or {},
                "created_at": datetime.now(timezone.utc),
            }
        )


class AdminAuthService:
    def __init__(self, repository, password_service, jwt_service, audit_logger):
        self.repository = repository
        self.password_service = password_service
        self.jwt_service = jwt_service
        self.audit_logger = audit_logger

    def register(self, data: dict) -> Admin:
        required = ["full_name", "email", "password", "role"]
        missing = [key for key in required if not data.get(key)]
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

    def login(self, email: str, password: str) -> dict:
        admin = self.repository.find_by_email(email)
        if not admin or not self.password_service.verify_password(password, admin.password_hash):
            self.audit_logger.log(email, "ADMIN_LOGIN_FAILED")
            raise ValueError("Invalid email or password")
        role = admin.role.value
        access_token = self.jwt_service.generate_access_token(admin, "admin", role)
        refresh_token = self.jwt_service.generate_refresh_token(admin, "admin", role)
        admin.sessions.append(
            Session(
                session_id=str(uuid4()),
                access_token=access_token,
                refresh_token=refresh_token,
                login_time=datetime.now(timezone.utc),
                expiry_time=datetime.now(timezone.utc) + timedelta(days=7),
            )
        )
        self.repository.update(admin)
        self.audit_logger.log(admin.admin_id, "ADMIN_LOGIN")
        return {"admin": admin, "access_token": access_token, "refresh_token": refresh_token}

    def logout(self, refresh_token: str) -> bool:
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


class AdminDashboardService:
    def __init__(self, users, admins, questions, performance, rag):
        self.users = users
        self.admins = admins
        self.questions = questions
        self.performance = performance
        self.rag = rag

    def summary(self) -> dict:
        return {
            "users": self.users.count(),
            "admins": self.admins.count(),
            "questions": self.questions.count_questions(),
            "mock_tests": self.questions.count_mock_tests(),
            "mock_test_attempts": self.performance.count(),
            "rag_documents": self.rag.count_documents(),
        }

    def users_overview(self, limit: int, skip: int) -> list[dict]:
        result = []
        for user in self.users.find_all(limit=limit, skip=skip):
            result.append(
                {
                    "user_id": user.user_id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "branch": user.branch.value,
                    "account_status": user.account_status.value,
                    "performance": self.performance.aggregate_user(user.user_id),
                }
            )
        return result
