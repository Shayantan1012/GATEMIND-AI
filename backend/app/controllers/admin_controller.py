from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, request
from werkzeug.utils import secure_filename

from app.schemas.serializers import (
    serialize_admin,
    serialize_mock_test,
    serialize_mock_test_with_questions,
    serialize_question,
)
from app.utils.auth import admin_required
from app.utils.responses import error_response, success_response

admin_bp = Blueprint("admin", __name__)


def services():
    return current_app.extensions["services"]


@admin_bp.post("/auth/register")
def register_admin():
    admin_count = services()["admins_repo"].count()
    if admin_count:
        return error_response("Only a logged-in Super Admin can create additional admins", 403)
    try:
        payload = request.get_json(silent=True) or {}
        payload["role"] = "SUPER_ADMIN"
        admin = services()["admin_auth"].register(payload)
        return success_response(serialize_admin(admin), "Admin registered", 201)
    except ValueError as error:
        return error_response(str(error), 400)


@admin_bp.post("/staff")
@admin_required("SUPER_ADMIN")
def create_admin_staff(current_admin):
    try:
        admin = services()["admin_auth"].register(request.get_json(silent=True) or {})
        return success_response(serialize_admin(admin), "Admin staff account created", 201)
    except ValueError as error:
        return error_response(str(error), 400)


@admin_bp.get("/staff")
@admin_required("SUPER_ADMIN")
def list_admin_staff(current_admin):
    staff = services()["admins_repo"].find_all()
    return success_response([serialize_admin(admin) for admin in staff])


@admin_bp.delete("/staff/<admin_id>")
@admin_required("SUPER_ADMIN")
def delete_admin_staff(current_admin, admin_id):
    if current_admin.admin_id == admin_id:
        return error_response("You cannot delete your own active admin account", 400)
    if not services()["admins_repo"].find_by_id(admin_id):
        return error_response("Admin staff account not found", 404)
    services()["admins_repo"].delete_by_id(admin_id)
    return success_response(message="Admin staff account deleted")


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
    try:
        limit = min(max(int(request.args.get("limit", 50)), 1), 200)
        skip = max(int(request.args.get("skip", 0)), 0)
    except ValueError:
        return error_response("limit and skip must be integers", 400)
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
        questions = services()["question_bank"].get_mock_test_questions(mock_test)
        return success_response(serialize_mock_test_with_questions(mock_test, questions), "Mock test created", 201)
    except (ValueError, KeyError) as error:
        return error_response(str(error), 400)


@admin_bp.get("/mock-tests")
@admin_required("MOCKTEST_ADMIN", "ANALYTICS_ADMIN")
def list_mock_tests(current_admin):
    mock_tests = services()["question_bank"].list_mock_tests()
    return success_response(
        [serialize_mock_test_with_questions(item, services()["question_bank"].get_mock_test_questions(item)) for item in mock_tests]
    )


@admin_bp.put("/mock-tests/<mock_test_id>")
@admin_required("MOCKTEST_ADMIN")
def update_mock_test(current_admin, mock_test_id):
    try:
        mock_test = services()["question_bank"].update_mock_test(
            mock_test_id,
            request.get_json(silent=True) or {},
            current_admin.admin_id,
        )
        questions = services()["question_bank"].get_mock_test_questions(mock_test)
        return success_response(serialize_mock_test_with_questions(mock_test, questions), "Mock test updated")
    except ValueError as error:
        status_code = 404 if str(error) == "Mock test not found" else 400
        return error_response(str(error), status_code)


@admin_bp.post("/mock-tests/<mock_test_id>/publish")
@admin_required("MOCKTEST_ADMIN")
def publish_mock_test(current_admin, mock_test_id):
    try:
        mock_test = services()["question_bank"].publish_mock_test(mock_test_id)
        return success_response(serialize_mock_test(mock_test), "Mock test published")
    except ValueError as error:
        return error_response(str(error), 404)


@admin_bp.delete("/mock-tests/<mock_test_id>")
@admin_required("MOCKTEST_ADMIN")
def delete_mock_test(current_admin, mock_test_id):
    try:
        services()["question_bank"].delete_mock_test(mock_test_id)
        return success_response(message="Mock test deleted")
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
        description = request.form.get("description", "")
        document = services()["rag_indexer"].execute(
            target,
            current_admin.admin_id,
            {
                "subject": request.form.get("subject", ""),
                "description": description,
                "original_name": uploaded_file.filename,
            },
        )
        document["description"] = description
        services()["rag_repo"].save_document(document)
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


@admin_bp.delete("/rag/documents/<document_id>")
@admin_required("CONTENT_ADMIN")
def delete_rag_document(current_admin, document_id):
    document = services()["rag_repo"].find_document(document_id)
    if not document:
        return error_response("Document not found", 404)
    services()["rag_repo"].delete_document(document_id)
    return success_response(message="Document deleted")


@admin_bp.delete("/maintenance/storage")
@admin_required("SUPER_ADMIN")
def clear_logs_and_uploaded_documents(current_admin):
    try:
        result = services()["storage_maintenance"].clear_logs_and_uploaded_documents()
        return success_response(result, "Logs and uploaded study documents cleared")
    except (OSError, ValueError) as error:
        return error_response(str(error), 500)
