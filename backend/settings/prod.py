################################
# backend/settings/prod.py
# Settings for Production-System
################################

from .base import *

DEBUG = False
load_dotenv("/var/www/sharegy/shared/.env")

env_allowed_hosts = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]
ALLOWED_HOSTS = list(set([
    "sharegy.de",
    "www.sharegy.de",
    "api.sharegy.de",
] + env_allowed_hosts))

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SAMESITE = "None"

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "https://sharegy.de",
    "https://www.sharegy.de",
    "http://localhost",
    "https://localhost",
    "capacitor://localhost",
    "https://de.sharegy.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://sharegy.de",
    "https://www.sharegy.de",
    "http://localhost",
    "https://localhost",
    "capacitor://localhost",
    "https://de.sharegy.app",
]
TRACKING_BASE_URL = os.getenv("TRACKING_BASE_URL", "https://api.sharegy.de")