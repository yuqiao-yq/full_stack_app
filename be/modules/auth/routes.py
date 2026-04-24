from flask import Blueprint, g, jsonify, request

from modules.auth.jwt_utils import build_token, require_auth
from modules.auth.service import AuthError, authenticate_user, register_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def error_response(message, status_code):
    return jsonify({"message": message}), status_code


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}

    try:
        user = register_user(
            username=payload.get("username"),
            password=payload.get("password"),
            confirm_password=payload.get("confirmPassword"),
            display_name=payload.get("displayName"),
        )
    except AuthError as error:
        return error_response(error.message, error.status_code)

    token = build_token(user)
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}

    try:
        user = authenticate_user(
            username=payload.get("username"),
            password=payload.get("password"),
        )
    except AuthError as error:
        return error_response(error.message, error.status_code)

    token = build_token(user)
    return jsonify({"token": token, "user": user.to_dict()})


@auth_bp.get("/me")
@require_auth
def get_current_user():
    return jsonify({"user": g.current_user.to_dict()})
