from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from core.extensions import db
from modules.auth.models import User


def unauthorized(message, status_code=401):
    return jsonify({"message": message}), status_code


def build_token(user):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "name": user.display_name,
        "iat": now,
        "exp": now + timedelta(hours=current_app.config["JWT_EXPIRES_IN_HOURS"]),
    }
    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def _decode_token(token):
    return jwt.decode(
        token,
        current_app.config["JWT_SECRET"],
        algorithms=[current_app.config["JWT_ALGORITHM"]],
    )


def require_auth(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.removeprefix("Bearer ").strip()

        if not token:
            return unauthorized("Missing authorization token")

        try:
            payload = _decode_token(token)
        except jwt.ExpiredSignatureError:
            return unauthorized("Token has expired")
        except jwt.InvalidTokenError:
            return unauthorized("Invalid token")

        user = db.session.get(User, int(payload["sub"]))
        if user is None:
            return unauthorized("User not found")

        g.current_user = user
        return view_func(*args, **kwargs)

    return wrapped_view
