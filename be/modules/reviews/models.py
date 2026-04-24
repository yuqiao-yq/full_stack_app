from datetime import datetime, timezone

from core.extensions import db


class GameReview(db.Model):
    __tablename__ = "game_reviews"

    __table_args__ = (
        db.UniqueConstraint("user_id", "external_game_id", name="uq_user_game_review"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    external_game_id = db.Column(db.String(50), nullable=False, index=True)
    game_name = db.Column(db.String(255), nullable=False)
    cover_url = db.Column(db.String(500))
    platforms = db.Column(db.JSON, nullable=False, default=list)
    genres = db.Column(db.JSON, nullable=False, default=list)
    released = db.Column(db.String(20))
    external_rating = db.Column(db.Float)
    user_score = db.Column(db.Float, nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="reviewed")
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "externalGameId": self.external_game_id,
            "gameName": self.game_name,
            "coverUrl": self.cover_url,
            "platforms": self.platforms or [],
            "genres": self.genres or [],
            "released": self.released,
            "externalRating": self.external_rating,
            "userScore": self.user_score,
            "reviewText": self.review_text,
            "status": self.status,
            "createdAt": self.created_at.isoformat(),
        }
