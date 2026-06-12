from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, request, send_from_directory
from werkzeug.utils import secure_filename

from app.schemas.serializers import serialize_profile
from app.utils.auth import token_required
from app.utils.responses import error_response, success_response

user_bp = Blueprint("users", __name__)
PROFILE_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def get_user_service():
    return current_app.extensions["services"]["users"]


@user_bp.get("/profile")
@token_required
def get_profile(current_user):
    try:
        user = current_user
        payload = serialize_profile(user.user_profile) or {}
        payload["branch"] = user.branch.value
        payload["full_name"] = user.full_name
        payload["email"] = user.email
        payload["mobile_number"] = user.mobile_number
        payload["target_gate_year"] = user.target_gate_year
        return success_response(payload)
    except ValueError as error:
        return error_response(str(error), 404)


@user_bp.put("/profile")
@token_required
def update_profile(current_user):
    try:
        user = get_user_service().update_profile(current_user.user_id, request.get_json(silent=True) or {})
        payload = serialize_profile(user.user_profile) or {}
        payload["branch"] = user.branch.value
        payload["full_name"] = user.full_name
        payload["email"] = user.email
        payload["mobile_number"] = user.mobile_number
        payload["target_gate_year"] = user.target_gate_year
        return success_response(payload, "Profile updated")
    except ValueError as error:
        return error_response(str(error), 400)


@user_bp.post("/profile/image")
@token_required
def upload_profile_image(current_user):
    uploaded_file = request.files.get("image")
    if not uploaded_file or not uploaded_file.filename:
        return error_response("image is required", 400)

    extension = Path(secure_filename(uploaded_file.filename)).suffix.lower()
    if extension not in PROFILE_IMAGE_EXTENSIONS:
        return error_response("Profile image must be JPG, PNG, or WEBP", 400)
    if uploaded_file.mimetype and not uploaded_file.mimetype.startswith("image/"):
        return error_response("Invalid image file", 400)

    filename = f"{current_user.user_id}-{uuid4()}{extension}"
    target_folder = Path(current_app.config["UPLOAD_FOLDER"]) / "profile-images"
    target_folder.mkdir(parents=True, exist_ok=True)
    uploaded_file.save(target_folder / filename)

    image_url = f"/api/users/profile-images/{filename}"
    user = get_user_service().update_profile_image(current_user.user_id, image_url)
    payload = serialize_profile(user.user_profile) or {}
    payload["branch"] = user.branch.value
    payload["full_name"] = user.full_name
    payload["email"] = user.email
    payload["mobile_number"] = user.mobile_number
    payload["target_gate_year"] = user.target_gate_year
    return success_response(payload, "Profile image updated")


@user_bp.get("/profile-images/<filename>")
def serve_profile_image(filename):
    target_folder = Path(current_app.config["UPLOAD_FOLDER"]) / "profile-images"
    return send_from_directory(target_folder, secure_filename(filename))


@user_bp.post("/change-password")
@token_required
def change_password(current_user):
    payload = request.get_json(silent=True) or {}
    try:
        get_user_service().change_password(
            current_user.user_id,
            payload.get("old_password", ""),
            payload.get("new_password", ""),
        )
        return success_response(message="Password changed")
    except ValueError as error:
        return error_response(str(error), 400)


@user_bp.get("/progress")
@token_required
def get_progress(current_user):
    try:
        return success_response(get_user_service().get_preparation_progress(current_user.user_id))
    except ValueError as error:
        return error_response(str(error), 404)


@user_bp.get("/mock-test-history")
@token_required
def get_mock_test_history(current_user):
    try:
        return success_response({"mock_test_history": get_user_service().get_mock_test_history(current_user.user_id)})
    except ValueError as error:
        return error_response(str(error), 404)
