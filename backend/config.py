import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INSTANCE_DIR = PROJECT_ROOT / 'instance'
INSTANCE_DIR.mkdir(exist_ok=True)
DEFAULT_DATABASE_URI = f"sqlite:///{(INSTANCE_DIR / 'dulceria.db').as_posix()}"


def _parse_cors_origins(value):
    if not value or value.strip() == "*":
        return "*"

    return [origin.strip() for origin in value.split(",") if origin.strip()]


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', DEFAULT_DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-cambiar-en-produccion')
    CORS_ORIGINS = _parse_cors_origins(os.getenv('CORS_ORIGINS', '*'))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
