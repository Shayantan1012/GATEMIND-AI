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
            user_id = jwt_service.extract_user_id(token)
        except jwt.ExpiredSignatureError:
            return error_response("Token has expired", 401)
        except jwt.InvalidTokenError:
            return error_response("Invalid token", 401)

        user = users_repo.find_by_id(user_id)
        if not user:
            return error_response("User not found", 401)
        return view(user, *args, **kwargs)

    return wrapped
