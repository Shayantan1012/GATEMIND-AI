from flask import Blueprint, current_app, request

from app.schemas.serializers import serialize_mock_test
from app.utils.auth import token_required
from app.utils.responses import error_response, success_response

mock_test_bp = Blueprint("mock_tests", __name__)


def service():
    return current_app.extensions["services"]["mock_tests"]


@mock_test_bp.get("")
@token_required
def list_mock_tests(current_user):
    return success_response([serialize_mock_test(item) for item in service().list_available()])


@mock_test_bp.get("/<mock_test_id>")
@token_required
def get_mock_test(current_user, mock_test_id):
    try:
        result = service().get_test(mock_test_id)
        return success_response(
            {
                "mock_test": serialize_mock_test(result["mock_test"]),
                "questions": result["questions"],
            }
        )
    except ValueError as error:
        return error_response(str(error), 404)


@mock_test_bp.post("/<mock_test_id>/submit")
@token_required
def submit_mock_test(current_user, mock_test_id):
    payload = request.get_json(silent=True) or {}
    try:
        return success_response(
            service().submit(
                current_user.user_id,
                mock_test_id,
                payload.get("answers", []),
                payload.get("time_taken_seconds", 0),
            ),
            "Mock test evaluated",
        )
    except ValueError as error:
        return error_response(str(error), 400)


@mock_test_bp.get("/history")
@token_required
def performance_history(current_user):
    return success_response(service().history(current_user.user_id))
