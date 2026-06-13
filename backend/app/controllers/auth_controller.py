import jwt
from flask import Blueprint, current_app, request

from app.schemas.serializers import serialize_user
from app.utils.responses import error_response, success_response

auth_bp = Blueprint("auth", __name__)


def get_auth_service():
    return current_app.extensions["services"]["auth"]


@auth_bp.post("/register")
def register():
    try:
        user, otp = get_auth_service().register_user(request.get_json(silent=True) or {})
        data = {"user": serialize_user(user)}
        if current_app.config["OTP_PREVIEW_ENABLED"]:
            data["preview_otp"] = otp
        return success_response(data, "User registered. OTP sent for verification.", 201)
    except ValueError as error:
        return error_response(str(error), 400)


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    try:
        auth_data = get_auth_service().authenticate_user(payload.get("email", ""), payload.get("password", ""))
        return success_response(
            {
                "user": serialize_user(auth_data["user"]),
                "access_token": auth_data["access_token"],
                "refresh_token": auth_data["refresh_token"],
            },
            "Login successful",
        )
    except ValueError as error:
        return error_response(str(error), 401)


@auth_bp.post("/logout")
def logout():
    payload = request.get_json(silent=True) or {}
    logged_out = get_auth_service().logout_user(payload.get("refresh_token", ""))
    if not logged_out:
        return error_response("Session not found", 404)
    return success_response(message="Logout successful")


@auth_bp.post("/forgot-password")
def forgot_password():
    payload = request.get_json(silent=True) or {}
    otp = get_auth_service().forgot_password(payload.get("email", ""))
    data = {"preview_otp": otp} if otp and current_app.config["OTP_PREVIEW_ENABLED"] else None
    return success_response(data=data, message="If the email exists, an OTP has been sent.")


@auth_bp.post("/verify-otp")
def verify_otp():
    payload = request.get_json(silent=True) or {}
    try:
        user = get_auth_service().verify_otp(payload.get("otp", ""))
        return success_response(serialize_user(user), "OTP verified")
    except ValueError as error:
        return error_response(str(error), 400)


@auth_bp.post("/refresh-token")
def refresh_token():
    payload = request.get_json(silent=True) or {}
    try:
        access_token = get_auth_service().refresh_token(payload.get("refresh_token", ""))
        return success_response({"access_token": access_token}, "Access token refreshed")
    except (ValueError, jwt.InvalidTokenError) as error:
        return error_response(str(error), 401)


@auth_bp.post("/reset-password")
def reset_password():
    payload = request.get_json(silent=True) or {}
    try:
        get_auth_service().reset_password(payload.get("otp", ""), payload.get("new_password", ""))
        return success_response(message="Password reset successful")
    except ValueError as error:
        return error_response(str(error), 400)
