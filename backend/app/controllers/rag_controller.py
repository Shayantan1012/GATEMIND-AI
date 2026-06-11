from flask import Blueprint, current_app, request

from app.utils.auth import token_required
from app.utils.responses import error_response, success_response

rag_bp = Blueprint("rag", __name__)


def service():
    return current_app.extensions["services"]["rag_chat"]


@rag_bp.post("/chat")
@token_required
def chat(current_user):
    payload = request.get_json(silent=True) or {}
    try:
        response = service().ask(
            current_user.user_id,
            payload.get("query", ""),
            payload.get("filters"),
        )
        return success_response(response.to_dict())
    except ValueError as error:
        return error_response(str(error), 400)


@rag_bp.get("/history")
@token_required
def chat_history(current_user):
    history = service().history(current_user.user_id)
    for item in history:
        if hasattr(item.get("created_at"), "isoformat"):
            item["created_at"] = item["created_at"].isoformat()
    return success_response(history)
