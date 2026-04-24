import re

from werkzeug.security import check_password_hash, generate_password_hash

from core.extensions import db
from modules.auth.models import User

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,20}$")
PASSWORD_LETTER_PATTERN = re.compile(r"[A-Za-z]")
PASSWORD_NUMBER_PATTERN = re.compile(r"\d")
PASSWORD_HASH_METHOD = "pbkdf2:sha256"


class AuthError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _normalize_username(username):
    return (username or "").strip()


def _normalize_display_name(username, display_name):
    value = (display_name or "").strip()
    return value or username


def validate_username(username):
    if not username:
        raise AuthError("Username is required")

    if not USERNAME_PATTERN.fullmatch(username):
        raise AuthError(
            "Username must be 3-20 characters and use only letters, numbers, or underscores",
        )


def validate_password(password):
    if not password:
        raise AuthError("Password is required")

    if len(password) < 8:
        raise AuthError("Password must be at least 8 characters long")

    if not PASSWORD_LETTER_PATTERN.search(password):
        raise AuthError("Password must include at least one letter")

    if not PASSWORD_NUMBER_PATTERN.search(password):
        raise AuthError("Password must include at least one number")


def validate_display_name(display_name):
    if not display_name:
        raise AuthError("Display name is required")

    if len(display_name) > 50:
        raise AuthError("Display name must be 50 characters or fewer")


def register_user(username, password, confirm_password=None, display_name=None):
    normalized_username = _normalize_username(username)
    normalized_display_name = _normalize_display_name(
        normalized_username,
        display_name,
    )

    validate_username(normalized_username)
    validate_password(password)
    validate_display_name(normalized_display_name)

    if confirm_password is not None and password != confirm_password:
        raise AuthError("Passwords do not match")

    existing_user = User.query.filter_by(username=normalized_username).first()
    if existing_user:
        raise AuthError("Username already exists", status_code=409)

    user = User(
        username=normalized_username,
        display_name=normalized_display_name,
        password_hash=generate_password_hash(
            password,
            method=PASSWORD_HASH_METHOD,
        ),
    )
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(username, password):
    normalized_username = _normalize_username(username)

    if not normalized_username or not password:
        raise AuthError("Username and password are required")

    user = User.query.filter_by(username=normalized_username).first()
    if not user or not check_password_hash(user.password_hash, password):
        raise AuthError("Invalid username or password", status_code=401)

    return user
