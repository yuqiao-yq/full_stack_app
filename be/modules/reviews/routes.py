from flask import Blueprint, g, jsonify, request

from modules.auth.jwt_utils import require_auth
from modules.reviews.service import (
    ReviewError,
    create_or_update_review,
    list_reviews_for_user,
)

reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")


@reviews_bp.get("/mine")
@require_auth
def mine():
    reviews = list_reviews_for_user(g.current_user.id)
    return jsonify({"reviews": [review.to_dict() for review in reviews]})


@reviews_bp.post("")
@require_auth
def create_or_update():
    payload = request.get_json(silent=True) or {}

    try:
        review, created = create_or_update_review(g.current_user.id, payload)
    except ReviewError as error:
        return jsonify({"message": error.message}), error.status_code

    return jsonify({"review": review.to_dict()}), 201 if created else 200
