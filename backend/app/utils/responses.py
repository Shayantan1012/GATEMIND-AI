from flask import jsonify


def success_response(data=None, message="Success", status_code=200):
    payload = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def error_response(message="Something went wrong", status_code=400):
    return jsonify({"success": False, "message": message}), status_code
