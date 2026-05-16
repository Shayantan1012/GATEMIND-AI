from flask import Blueprint, current_app, request

from app.schemas.serializers import serialize_profile
from app.utils.auth import token_required
from app.utils.responses import error_response, success_response

user_bp = Blueprint("users", __name__)


def get_user_service():
    return current_app.extensions["services"]["users"]


@user_bp.get("/profile")
@token_required
def get_profile(current_user):
    try:
        profile = get_user_service().get_user_profile(current_user.user_id)
        return success_response(serialize_profile(profile))
    except ValueError as error:
        return error_response(str(error), 404)


@user_bp.put("/profile")
@token_required
def update_profile(current_user):
    try:
        profile = get_user_service().update_profile(current_user.user_id, request.get_json(silent=True) or {})
        return success_response(serialize_profile(profile), "Profile updated")
    except ValueError as error:
        return error_response(str(error), 404)


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
