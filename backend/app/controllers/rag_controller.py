from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, request
from werkzeug.utils import secure_filename

from app.utils.auth import token_required
from app.utils.responses import error_response, success_response

rag_bp = Blueprint("rag", __name__)


def service():
    return current_app.extensions["services"]["rag_chat"]


def serialize_document(document):
    result = dict(document)
    if hasattr(result.get("uploaded_at"), "isoformat"):
        result["uploaded_at"] = result["uploaded_at"].isoformat()
    return result


def serialize_conversation(conversation):
    result = dict(conversation)
    result["conversation_id"] = result.pop("_id")
    for field in ("created_at", "updated_at"):
        if hasattr(result.get(field), "isoformat"):
            result[field] = result[field].isoformat()
    return result


def serialize_chat(chat):
    result = dict(chat)
    if hasattr(result.get("created_at"), "isoformat"):
        result["created_at"] = result["created_at"].isoformat()
    return result


@rag_bp.post("/documents")
@token_required
def upload_documents(current_user):
    uploaded_files = [item for item in request.files.getlist("files") if item and item.filename]
    if not uploaded_files:
        single_file = request.files.get("file")
        uploaded_files = [single_file] if single_file and single_file.filename else []
    if not uploaded_files:
        return error_response("At least one file is required", 400)
    if len(uploaded_files) > 5:
        return error_response("A maximum of 5 files can be attached at once", 400)

    documents = []
    for uploaded_file in uploaded_files:
        filename = f"{uuid4()}-{secure_filename(uploaded_file.filename)}"
        target = Path(current_app.config["UPLOAD_FOLDER"]) / "users" / current_user.user_id / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        uploaded_file.save(target)
        try:
            document = current_app.extensions["services"]["rag_indexer"].execute(
                target,
                current_user.user_id,
                {
                    "owner_type": "user",
                    "original_name": uploaded_file.filename,
                    "subject": request.form.get("subject", ""),
                },
            )
            documents.append(serialize_document(document))
        except ValueError as error:
            return error_response(str(error), 400)
    return success_response(documents, "Files uploaded and indexed", 201)


@rag_bp.get("/documents")
@token_required
def list_user_documents(current_user):
    documents = current_app.extensions["services"]["rag_repo"].list_documents_by_uploader(current_user.user_id)
    return success_response([serialize_document(item) for item in documents])


@rag_bp.post("/chat")
@token_required
def chat(current_user):
    payload = request.get_json(silent=True) or {}
    try:
        response, conversation = service().ask(
            current_user.user_id,
            payload.get("query", ""),
            payload.get("filters"),
            payload.get("conversation_id"),
        )
        return success_response(
            {
                **response.to_dict(),
                "conversation": serialize_conversation(conversation),
            }
        )
    except ValueError as error:
        return error_response(str(error), 400)


@rag_bp.post("/conversations")
@token_required
def create_conversation(current_user):
    payload = request.get_json(silent=True) or {}
    return success_response(
        serialize_conversation(service().create_conversation(current_user.user_id, payload.get("title", "New chat"))),
        "Conversation created",
        201,
    )


@rag_bp.get("/conversations")
@token_required
def list_conversations(current_user):
    return success_response([serialize_conversation(item) for item in service().conversations(current_user.user_id)])


@rag_bp.get("/conversations/<conversation_id>/messages")
@token_required
def conversation_messages(current_user, conversation_id):
    try:
        return success_response([serialize_chat(item) for item in service().history(current_user.user_id, conversation_id)])
    except ValueError as error:
        return error_response(str(error), 404)


@rag_bp.get("/history")
@token_required
def chat_history(current_user):
    return success_response([serialize_chat(item) for item in service().history(current_user.user_id)])


@rag_bp.delete("/conversations/<conversation_id>")
@token_required
def delete_conversation(current_user, conversation_id):
    payload = request.get_json(silent=True) or {}
    try:
        service().delete_conversation(current_user.user_id, conversation_id, payload.get("document_ids"))
        return success_response(message="Conversation deleted")
    except ValueError as error:
        return error_response(str(error), 404)
