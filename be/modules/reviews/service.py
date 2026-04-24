from core.extensions import db
from modules.reviews.models import GameReview

VALID_REVIEW_STATUSES = {"reviewed", "wishlist", "played", "completed"}


class ReviewError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def list_reviews_for_user(user_id):
    return (
        GameReview.query.filter_by(user_id=user_id)
        .order_by(GameReview.created_at.desc())
        .all()
    )


def create_or_update_review(user_id, payload):
    external_game_id = str(payload.get("externalGameId", "")).strip()
    game_name = (payload.get("gameName") or "").strip()
    review_text = (payload.get("reviewText") or "").strip()
    status = (payload.get("status") or "reviewed").strip()
    cover_url = payload.get("coverUrl")
    platforms = payload.get("platforms") or []
    genres = payload.get("genres") or []
    released = payload.get("released")
    external_rating = payload.get("externalRating")
    user_score = payload.get("userScore")

    if not external_game_id or not game_name:
        raise ReviewError("Game information is required")

    if not review_text:
        raise ReviewError("Review content is required")

    try:
        user_score = float(user_score)
    except (TypeError, ValueError) as error:
        raise ReviewError("User score must be a number") from error

    if not 0 <= user_score <= 5:
        raise ReviewError("User score must be between 0 and 5")

    if status not in VALID_REVIEW_STATUSES:
        raise ReviewError("Invalid review status")

    review = GameReview.query.filter_by(
        user_id=user_id,
        external_game_id=external_game_id,
    ).first()

    created = review is None
    if review is None:
        review = GameReview(
            user_id=user_id,
            external_game_id=external_game_id,
        )
        db.session.add(review)

    review.game_name = game_name
    review.cover_url = cover_url
    review.platforms = platforms
    review.genres = genres
    review.released = released
    review.external_rating = external_rating
    review.user_score = user_score
    review.review_text = review_text
    review.status = status
    db.session.commit()

    return review, created
