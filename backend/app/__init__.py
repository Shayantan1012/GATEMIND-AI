from flask import Flask, jsonify
from pymongo import MongoClient

from app.config import Config
from app.controllers.admin_controller import admin_bp
from app.controllers.auth_controller import auth_bp
from app.controllers.mock_test_controller import mock_test_bp
from app.controllers.rag_controller import rag_bp
from app.controllers.user_controller import user_bp
from app.repositories.mongo_user_repository import MongoUserRepository
from app.repositories.module_repositories import (
    MongoAdminRepository,
    MongoAuditRepository,
    MongoPerformanceRepository,
    MongoQuestionRepository,
    MongoRAGRepository,
)
from app.services.admin.admin_service import AdminAuthService, AdminDashboardService, AuditLogger
from app.services.auth_service import AuthenticationService
from app.services.jwt_service import JWTService
from app.services.mocktest.evaluation import QuestionEvaluator
from app.services.mocktest.mock_test_service import (
    MockTestService,
    PerformanceAnalyzer,
    PersonalizedRAGUpdater,
    QuestionBankService,
)
from app.services.otp_verification_service import OTPVerificationService
from app.services.password_service import PasswordService
from app.services.rag.document_processing import DocumentParserFactory, RecursiveChunkingStrategy
from app.services.rag.embedding_service import EmbeddingFactory, MongoVectorStoreAdapter
from app.services.rag.rag_service import (
    ContextBuilder,
    HybridReranker,
    LangChainIndexingPipeline,
    LLMService,
    RAGChatService,
)
from app.services.sms_notification_service import SMSNotificationService
from app.services.user_service import UserService


def create_app(config_class=Config, database=None):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if database is None:
        if app.config["MONGO_USE_MOCK"]:
            import mongomock

            mongo_client = mongomock.MongoClient()
        else:
            mongo_client = MongoClient(app.config["MONGO_URI"])
        database = mongo_client[app.config["MONGO_DB_NAME"]]
    db = database

    user_repository = MongoUserRepository(db)
    admin_repository = MongoAdminRepository(db)
    question_repository = MongoQuestionRepository(db)
    performance_repository = MongoPerformanceRepository(db)
    rag_repository = MongoRAGRepository(db)
    audit_repository = MongoAuditRepository(db)

    password_service = PasswordService()
    jwt_service = JWTService(app.config["SECRET_KEY"])
    sms_notification_service = SMSNotificationService(app.config)
    otp_verification_service = OTPVerificationService(sms_notification_service)
    audit_logger = AuditLogger(audit_repository)

    auth_service = AuthenticationService(
        user_repository=user_repository,
        password_service=password_service,
        jwt_service=jwt_service,
        verification_service=otp_verification_service,
    )
    user_service = UserService(user_repository, password_service)
    admin_auth_service = AdminAuthService(admin_repository, password_service, jwt_service, audit_logger)
    admin_dashboard_service = AdminDashboardService(
        user_repository,
        admin_repository,
        question_repository,
        performance_repository,
        rag_repository,
    )
    question_bank_service = QuestionBankService(question_repository)
    mock_test_service = MockTestService(
        question_repository,
        performance_repository,
        QuestionEvaluator(),
        PerformanceAnalyzer(),
        PersonalizedRAGUpdater(user_repository),
    )

    embeddings = EmbeddingFactory.create(app.config)
    vector_store = MongoVectorStoreAdapter(rag_repository)
    rag_indexer = LangChainIndexingPipeline(
        rag_repository,
        vector_store,
        embeddings,
        DocumentParserFactory,
        RecursiveChunkingStrategy(app.config["RAG_CHUNK_SIZE"], app.config["RAG_CHUNK_OVERLAP"]),
    )
    rag_chat_service = RAGChatService(
        rag_repository,
        vector_store,
        embeddings,
        HybridReranker(),
        ContextBuilder(),
        LLMService(app.config),
        user_repository,
        app.config["RAG_TOP_K"],
    )

    app.extensions["services"] = {
        "auth": auth_service,
        "users": user_service,
        "jwt": jwt_service,
        "users_repo": user_repository,
        "admins_repo": admin_repository,
        "admin_auth": admin_auth_service,
        "admin_dashboard": admin_dashboard_service,
        "question_bank": question_bank_service,
        "mock_tests": mock_test_service,
        "rag_indexer": rag_indexer,
        "rag_chat": rag_chat_service,
        "rag_repo": rag_repository,
    }

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(mock_test_bp, url_prefix="/api/mock-tests")
    app.register_blueprint(rag_bp, url_prefix="/api/rag")

    @app.get("/api/health")
    def health_check():
        return jsonify(
            {
                "status": "ok",
                "service": "gatemind-backend",
                "modules": ["auth", "users", "admin", "mock-tests", "rag"],
            }
        )

    return app
