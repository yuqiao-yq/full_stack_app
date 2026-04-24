import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _build_database_uri():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    user = os.getenv("MYSQL_USER", "root")
    password = quote_plus(os.getenv("MYSQL_PASSWORD", ""))
    database = os.getenv("MYSQL_DATABASE", "full_stack_app")

    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRES_IN_HOURS = int(os.getenv("JWT_EXPIRES_IN_HOURS", "24"))
    IGDB_CLIENT_ID = os.getenv("IGDB_CLIENT_ID", "")
    IGDB_CLIENT_SECRET = os.getenv("IGDB_CLIENT_SECRET", "")
    IGDB_AUTH_URL = os.getenv(
        "IGDB_AUTH_URL",
        "https://id.twitch.tv/oauth2/token",
    )
    IGDB_BASE_URL = os.getenv("IGDB_BASE_URL", "https://api.igdb.com/v4")
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
