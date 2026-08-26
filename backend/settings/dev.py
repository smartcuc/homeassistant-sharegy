#########################
# backend/settings/dev.py
# Settings for Dev-System
#########################

from .base import *

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
CORS_ALLOW_CREDENTIALS = True


DEBUG = True

TRACKING_ENABLED = not DEBUG

TRACKING_BASE_URL = (
    "http://localhost:8000" if DEBUG
    else "https://api.sharegy.de"
)
