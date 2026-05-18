from flask import Flask, jsonify
from pymongo import MongoClient

from app.config import Config
from app.controllers.auth_controller import auth_bp
from app.controllers.user_controller import user_bp
from app.repositories.mongo_user_repository import MongoUserRepository
from app.services.auth_service import AuthenticationService
from app.services.jwt_service import JWTService
from app.services.otp_verification_service import OTPVerificationService
from app.services.password_service import PasswordService
from app.services.sms_notification_service import SMSNotificationService
from app.services.user_service import UserService


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo_client = MongoClient(app.config["MONGO_URI"])
    db = mongo_client[app.config["MONGO_DB_NAME"]]
    user_repository = MongoUserRepository(db)
    password_service = PasswordService()
    jwt_service = JWTService(app.config["SECRET_KEY"])
    sms_notification_service = SMSNotificationService(app.config)
    otp_verification_service = OTPVerificationService(sms_notification_service)

    auth_service = AuthenticationService(
        user_repository=user_repository,
        password_service=password_service,
        jwt_service=jwt_service,
        verification_service=otp_verification_service,
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
