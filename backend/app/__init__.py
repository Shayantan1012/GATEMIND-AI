from flask import Flask, jsonify, request
from pymongo import MongoClient

from app.config import Config
from app.controllers.admin_controller import admin_bp
from app.controllers.auth_controller import auth_bp
from app.controllers.mock_test_controller import mock_test_bp
from app.controllers.rag_controller import rag_bp
from app.controllers.user_controller import user_bp
from app.repositories.mongo_user_repository import MongoUserRepository
from app.repositories.mongo_admin_repository import MongoAdminRepository
from app.repositories.mongo_audit_repository import MongoAuditRepository
from app.repositories.mongo_performance_repository import MongoPerformanceRepository
from app.repositories.mongo_question_repository import MongoQuestionRepository
from app.repositories.mongo_rag_repository import MongoRAGRepository
from app.services.admin.admin_auth_service import AdminAuthService
from app.services.admin.admin_dashboard_service import AdminDashboardService
from app.services.admin.audit_logger import AuditLogger
from app.services.admin.storage_maintenance_service import StorageMaintenanceService
from app.services.auth.authentication_service import AuthenticationService
from app.services.security.jwt_service import JWTService
from app.services.mocktest.mock_test_application_service import MockTestService
from app.services.mocktest.performance_analyzer import PerformanceAnalyzer
from app.services.mocktest.personalized_rag_updater import PersonalizedRAGUpdater
from app.services.mocktest.question_bank_service import QuestionBankService
from app.services.mocktest.question_evaluator import QuestionEvaluator
from app.services.security.password_service import PasswordService
from app.services.verification.otp_verification_service import OTPVerificationService
from app.services.rag.chunking.recursive_chunking_strategy import RecursiveChunkingStrategy
from app.services.rag.context_builder import ContextBuilder
from app.services.rag.embeddings.embedding_factory import EmbeddingFactory
from app.services.rag.indexing.langchain_indexing_pipeline import LangChainIndexingPipeline
from app.services.rag.llm_service_factory import LLMServiceFactory
from app.services.rag.parsers.document_parser_factory import DocumentParserFactory
from app.services.rag.rag_chat_service import RAGChatService
from app.services.rag.retrievers.hybrid_reranker import HybridReranker
from app.services.rag.retrievers.hybrid_retriever import HybridRetriever
from app.services.rag.vectorstores.mongo_vector_store_adapter import MongoVectorStoreAdapter
from app.services.notifications.sms_notification_service import SMSNotificationService
from app.services.users.user_service import UserService
from app.utils.logging_config import configure_file_logging


def create_app(config_class=Config, database=None):
    app = Flask(__name__)
    app.config.from_object(config_class)
    configure_file_logging(app)

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        if origin and origin in app.config["ALLOWED_ORIGINS"]:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Admin-Bootstrap-Token"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Vary"] = "Origin"
        return response

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
    storage_maintenance_service = StorageMaintenanceService(
        app.config["UPLOAD_FOLDER"],
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
        HybridRetriever(vector_store, embeddings, app.config["RAG_TOP_K"]),
        HybridReranker(),
        ContextBuilder(),
        LLMServiceFactory.create(app.config),
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
        "storage_maintenance": storage_maintenance_service,
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
