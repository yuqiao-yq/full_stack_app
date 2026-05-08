import json
import re
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import current_app

_token_cache = {
    "access_token": "",
    "expires_at": 0.0,
}

_translation_cache = {}

PLATFORM_TRANSLATIONS = {
    "PC (Microsoft Windows)": "PC",
    "Mac": "Mac",
    "Linux": "Linux",
    "Nintendo Switch": "任天堂 Switch",
    "Nintendo Switch 2": "任天堂 Switch 2",
    "PlayStation 4": "PlayStation 4",
    "PlayStation 5": "PlayStation 5",
    "PlayStation VR2": "PlayStation VR2",
    "Xbox One": "Xbox One",
    "Xbox Series X|S": "Xbox Series X|S",
    "iOS": "iOS",
    "Android": "Android",
    "Web browser": "网页",
}

GENRE_TRANSLATIONS = {
    "Adventure": "冒险",
    "Arcade": "街机",
    "Card & Board Game": "卡牌桌游",
    "Fighting": "格斗",
    "Hack and slash/Beat 'em up": "砍杀",
    "Indie": "独立",
    "MOBA": "多人在线战术竞技",
    "Music": "音乐",
    "Pinball": "弹球",
    "Platform": "平台跳跃",
    "Point-and-click": "点击冒险",
    "Puzzle": "益智",
    "Quiz/Trivia": "问答",
    "Racing": "竞速",
    "Real Time Strategy (RTS)": "即时战略",
    "Role-playing (RPG)": "角色扮演",
    "Shooter": "射击",
    "Simulator": "模拟",
    "Sport": "体育",
    "Strategy": "策略",
    "Tactical": "战术",
    "Turn-based strategy (TBS)": "回合策略",
    "Visual Novel": "视觉小说",
}


class GameProviderError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _contains_cjk(value):
    return bool(re.search(r"[\u4e00-\u9fff]", value or ""))


def _localize_platform_name(name):
    return PLATFORM_TRANSLATIONS.get(name, name)


def _localize_genre_name(name):
    return GENRE_TRANSLATIONS.get(name, name)


def _translate_text_to_zh(text):
    cleaned_text = (text or "").strip()
    if not cleaned_text:
        return None

    if _contains_cjk(cleaned_text):
        return cleaned_text

    cached = _translation_cache.get(cleaned_text)
    if cached is not None:
        return cached

    params = urlencode(
        {
            "client": "gtx",
            "sl": "auto",
            "tl": "zh-CN",
            "dt": "t",
            "q": cleaned_text,
        }
    )
    request = Request(
        f"https://translate.googleapis.com/translate_a/single?{params}",
        headers={
            "Accept": "application/json",
            "User-Agent": "full-stack-app/1.0",
        },
    )

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, json.JSONDecodeError):
        _translation_cache[cleaned_text] = None
        return None

    translated_text = "".join(
        part[0] for part in payload[0] if isinstance(part, list) and part and part[0]
    ).strip()
    _translation_cache[cleaned_text] = translated_text or None
    return _translation_cache[cleaned_text]


def _format_release_date(timestamp):
    if not timestamp:
        return None

    return datetime.fromtimestamp(timestamp, tz=timezone.utc).date().isoformat()


def _build_cover_url(cover):
    if not cover or not cover.get("url"):
        return None

    url = cover["url"].replace("t_thumb", "t_cover_big")
    return f"https:{url}" if url.startswith("//") else url


def _normalize_game(raw_game):
    name = raw_game["name"]
    summary = raw_game.get("summary")

    return {
        "externalGameId": str(raw_game["id"]),
        "name": name,
        "nameZh": _translate_text_to_zh(name),
        "coverUrl": _build_cover_url(raw_game.get("cover")),
        "released": _format_release_date(raw_game.get("first_release_date")),
        "rating": round(raw_game["rating"], 1) if raw_game.get("rating") else None,
        "platforms": [
            _localize_platform_name(item["name"])
            for item in raw_game.get("platforms", [])
            if item.get("name")
        ],
        "genres": [
            _localize_genre_name(item["name"])
            for item in raw_game.get("genres", [])
            if item.get("name")
        ],
        "summary": summary,
        "summaryZh": _translate_text_to_zh(summary),
    }


def _fetch_access_token():
    client_id = current_app.config.get("IGDB_CLIENT_ID")
    client_secret = current_app.config.get("IGDB_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise GameProviderError(
            "IGDB credentials are not configured. Please set IGDB_CLIENT_ID and IGDB_CLIENT_SECRET.",
            status_code=500,
        )

    body = urlencode(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }
    ).encode("utf-8")
    request = Request(
        current_app.config["IGDB_AUTH_URL"],
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise GameProviderError("Failed to fetch IGDB OAuth token") from error
    except URLError as error:
        raise GameProviderError("Unable to reach Twitch OAuth service") from error

    _token_cache["access_token"] = payload["access_token"]
    _token_cache["expires_at"] = time.time() + int(payload.get("expires_in", 0)) - 60
    return _token_cache["access_token"]


def _get_access_token():
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    return _fetch_access_token()


def search_games(query):
    cleaned_query = (query or "").strip()
    if not cleaned_query:
        raise GameProviderError("Search keyword is required", status_code=400)

    access_token = _get_access_token()
    request_body = (
        f'search "{cleaned_query}";'
        " fields id,name,summary,rating,first_release_date,cover.url,platforms.name,genres.name;"
        " limit 8;"
    ).encode("utf-8")
    request = Request(
        f"{current_app.config['IGDB_BASE_URL']}/games",
        data=request_body,
        headers={
            "Client-ID": current_app.config["IGDB_CLIENT_ID"],
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "text/plain",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise GameProviderError("Failed to fetch game data from IGDB") from error
    except URLError as error:
        raise GameProviderError("Unable to reach IGDB service") from error

    return [_normalize_game(item) for item in payload]
