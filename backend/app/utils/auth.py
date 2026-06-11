from functools import wraps

import jwt
from flask import current_app, request

from app.utils.responses import error_response


def get_bearer_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.removeprefix("Bearer ").strip()


def token_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        token = get_bearer_token()
        if not token:
            return error_response("Missing bearer token", 401)

        jwt_service = current_app.extensions["services"]["jwt"]
        users_repo = current_app.extensions["services"]["users_repo"]
        try:
            payload = jwt_service.extract_subject(token)
        except jwt.ExpiredSignatureError:
            return error_response("Token has expired", 401)
        except jwt.InvalidTokenError:
            return error_response("Invalid token", 401)
        if payload.get("type") != "access" or payload.get("subject_type", "user") != "user":
            return error_response("User access token required", 401)

        user_id = payload["sub"]
        user = users_repo.find_by_id(user_id)
        if not user:
            return error_response("User not found", 401)
        return view(user, *args, **kwargs)

    return wrapped


def admin_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            token = get_bearer_token()
            if not token:
                return error_response("Missing bearer token", 401)

            services = current_app.extensions["services"]
            try:
                payload = services["jwt"].extract_subject(token)
            except jwt.ExpiredSignatureError:
                return error_response("Token has expired", 401)
            except jwt.InvalidTokenError:
                return error_response("Invalid token", 401)

            if payload.get("subject_type") != "admin":
                return error_response("Admin access required", 403)
            if payload.get("type") != "access":
                return error_response("Admin access token required", 401)
            admin = services["admins_repo"].find_by_id(payload["sub"])
            if not admin:
                return error_response("Admin not found", 401)
            if allowed_roles and admin.role.value not in allowed_roles and admin.role.value != "SUPER_ADMIN":
                return error_response("Insufficient admin permissions", 403)
            return view(admin, *args, **kwargs)

        return wrapped

    return decorator
