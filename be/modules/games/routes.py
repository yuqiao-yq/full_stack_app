from flask import Blueprint, jsonify, request

from modules.auth.jwt_utils import require_auth
from modules.games.service import GameProviderError, search_games

games_bp = Blueprint("games", __name__, url_prefix="/api/games")


@games_bp.get("/search")
@require_auth
def search():
    query = request.args.get("q", "")

    try:
        results = search_games(query)
    except GameProviderError as error:
        return jsonify({"message": error.message}), error.status_code

    return jsonify({"results": results})
