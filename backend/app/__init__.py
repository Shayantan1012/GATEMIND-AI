from flask import Flask, jsonify

from app.config import Config
from app.controllers.auth_controller import auth_bp
from app.controllers.user_controller import user_bp
from app.repositories.user_repository import InMemoryUserRepository
from app.services.auth_service import AuthenticationService
from app.services.email_notification_service import EmailNotificationService
from app.services.email_verification_service import EmailVerificationService
from app.services.jwt_service import JWTService
from app.services.password_service import PasswordService
from app.services.user_service import UserService


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    user_repository = InMemoryUserRepository()
    password_service = PasswordService()
    jwt_service = JWTService(app.config["SECRET_KEY"])
    email_notification_service = EmailNotificationService()
    email_verification_service = EmailVerificationService(email_notification_service)

    auth_service = AuthenticationService(
        user_repository=user_repository,
        password_service=password_service,
        jwt_service=jwt_service,
        verification_service=email_verification_service,
    )
    user_service = UserService(user_repository, password_service)

    app.extensions["services"] = {
        "auth": auth_service,
        "users": user_service,
        "jwt": jwt_service,
        "users_repo": user_repository,
    }

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")

    @app.get("/api/health")
    def health_check():
        return jsonify({"status": "ok", "service": "gatemind-backend"})

    return app
