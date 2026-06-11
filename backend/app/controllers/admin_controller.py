from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, request
from werkzeug.utils import secure_filename

from app.schemas.serializers import serialize_admin, serialize_mock_test, serialize_question
from app.utils.auth import admin_required
from app.utils.responses import error_response, success_response

admin_bp = Blueprint("admin", __name__)


def services():
    return current_app.extensions["services"]


@admin_bp.post("/auth/register")
def register_admin():
    admin_count = services()["admins_repo"].count()
    bootstrap_token = current_app.config.get("ADMIN_BOOTSTRAP_TOKEN", "")
    if admin_count and (
        not bootstrap_token or request.headers.get("X-Admin-Bootstrap-Token") != bootstrap_token
    ):
        return error_response("Admin bootstrap token required", 403)
    try:
        admin = services()["admin_auth"].register(request.get_json(silent=True) or {})
        return success_response(serialize_admin(admin), "Admin registered", 201)
    except ValueError as error:
        return error_response(str(error), 400)


@admin_bp.post("/auth/login")
def login_admin():
    payload = request.get_json(silent=True) or {}
    try:
        result = services()["admin_auth"].login(payload.get("email", ""), payload.get("password", ""))
        return success_response(
            {
                "admin": serialize_admin(result["admin"]),
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
            },
            "Admin login successful",
        )
    except ValueError as error:
        return error_response(str(error), 401)


@admin_bp.post("/auth/logout")
@admin_required()
def logout_admin(current_admin):
    payload = request.get_json(silent=True) or {}
    if not services()["admin_auth"].logout(payload.get("refresh_token", "")):
        return error_response("Session not found", 404)
    return success_response(message="Admin logout successful")


@admin_bp.post("/auth/refresh-token")
def refresh_admin_token():
    payload = request.get_json(silent=True) or {}
    try:
        token = services()["jwt"].refresh_token(payload.get("refresh_token", ""))
        subject = services()["jwt"].extract_subject(token)
        if subject.get("subject_type") != "admin":
            return error_response("Admin refresh token required", 403)
        return success_response({"access_token": token}, "Admin access token refreshed")
    except Exception:
        return error_response("Invalid or expired refresh token", 401)


@admin_bp.get("/dashboard")
@admin_required("ANALYTICS_ADMIN")
def dashboard(current_admin):
    return success_response(services()["admin_dashboard"].summary())


@admin_bp.get("/users")
@admin_required("ANALYTICS_ADMIN", "SUPPORT_ADMIN")
def users_overview(current_admin):
    limit = min(int(request.args.get("limit", 50)), 200)
    skip = max(int(request.args.get("skip", 0)), 0)
    return success_response(services()["admin_dashboard"].users_overview(limit, skip))


@admin_bp.post("/questions")
@admin_required("CONTENT_ADMIN", "MOCKTEST_ADMIN")
def create_question(current_admin):
    try:
        question = services()["question_bank"].create_question(
            request.get_json(silent=True) or {},
            current_admin.admin_id,
        )
        return success_response(serialize_question(question, include_answer=True), "Question created", 201)
    except (ValueError, KeyError) as error:
        return error_response(str(error), 400)


@admin_bp.get("/questions")
@admin_required("CONTENT_ADMIN", "MOCKTEST_ADMIN")
def list_questions(current_admin):
    questions = services()["question_bank"].list_questions(request.args.get("subject"))
    return success_response([serialize_question(item, include_answer=True) for item in questions])


@admin_bp.post("/mock-tests")
@admin_required("MOCKTEST_ADMIN")
def create_mock_test(current_admin):
    try:
        mock_test = services()["question_bank"].create_mock_test(
            request.get_json(silent=True) or {},
            current_admin.admin_id,
        )
        return success_response(serialize_mock_test(mock_test), "Mock test created", 201)
    except (ValueError, KeyError) as error:
        return error_response(str(error), 400)


@admin_bp.post("/mock-tests/<mock_test_id>/publish")
@admin_required("MOCKTEST_ADMIN")
def publish_mock_test(current_admin, mock_test_id):
    try:
        mock_test = services()["question_bank"].publish_mock_test(mock_test_id)
        return success_response(serialize_mock_test(mock_test), "Mock test published")
    except ValueError as error:
        return error_response(str(error), 404)


@admin_bp.post("/rag/documents")
@admin_required("CONTENT_ADMIN")
def upload_rag_document(current_admin):
    uploaded_file = request.files.get("file")
    if not uploaded_file or not uploaded_file.filename:
        return error_response("file is required", 400)
    filename = f"{uuid4()}-{secure_filename(uploaded_file.filename)}"
    target = Path(current_app.config["UPLOAD_FOLDER"]) / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    uploaded_file.save(target)
    try:
        document = services()["rag_indexer"].execute(
            target,
            current_admin.admin_id,
            {"subject": request.form.get("subject", ""), "original_name": uploaded_file.filename},
        )
        document["uploaded_at"] = document["uploaded_at"].isoformat()
        return success_response(document, "Document indexed", 201)
    except ValueError as error:
        return error_response(str(error), 400)


@admin_bp.get("/rag/documents")
@admin_required("CONTENT_ADMIN", "ANALYTICS_ADMIN")
def list_rag_documents(current_admin):
    documents = services()["rag_repo"].list_documents()
    for document in documents:
        if hasattr(document.get("uploaded_at"), "isoformat"):
            document["uploaded_at"] = document["uploaded_at"].isoformat()
    return success_response(documents)
