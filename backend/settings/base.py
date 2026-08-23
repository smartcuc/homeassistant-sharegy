###########################
# backend/settings/base.py
# Settings for All-System
###########################

# backend/settings/base.py

from pathlib import Path
from dotenv import load_dotenv
import os

from celery.schedules import crontab
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


BASE_DIR = Path(__file__).resolve().parents[2]

if os.path.exists("/var/www/sharegy/shared/.env"):
    load_dotenv("/var/www/sharegy/shared/.env")  # ✅ Server
else:
    load_dotenv(BASE_DIR / ".env")  # ✅ Lokal


# =============================
# Core Settings
# =============================

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-in-production")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

allowed_hosts_raw = os.getenv("ALLOWED_HOSTS", "*")
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_raw.split(",") if h.strip()]

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


# =============================
# Session / Security
# =============================

SESSION_COOKIE_AGE = 60 * 60 * 24 * 30
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"

CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "False") == "True"


# =============================
# CORS / CSRF
# =============================

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]


# =============================
# DRF
# =============================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.auth.CsrfExemptSessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}


# =============================
# HTTPS / Security Headers
# =============================

HTTPS = os.getenv("HTTPS", "False") == "True"

SECURE_SSL_REDIRECT = HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if HTTPS:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    SECURE_HSTS_SECONDS = 0


# =============================
# Email
# =============================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 465))
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "Sharegy <invite@sharegy.cloud>"
)


# =============================
# Apps
# =============================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "django_celery_results",
    "rest_framework",  # ✅ hinzufügen
    "rest_framework_simplejwt",
    "corsheaders",
    "devices.apps.DevicesConfig",
    "core",
    "integrations",  # ✅ DAS IST WICHTIG
    "tenants",
    "content",
    "design",
    "demo",
    "channels",
    "forecast",
    "accounts",
    "billing",
    "market",
    "producer",
    "user_settings",
    "energy",
    "operations",
    "tracking",
    "providers.opentelemetry",
]


# =============================
# Middleware
# =============================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",

    "core.middleware.RequestIdMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "backend.urls"
WSGI_APPLICATION = "backend.wsgi.application"


# =============================
# Templates
# =============================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =============================
# Database
# =============================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 60,
    }
}


# =============================
# Auth
# =============================

AUTH_USER_MODEL = "accounts.User"


# =============================
# Internationalization
# =============================

USE_I18N = True
LANGUAGE_CODE = "de-DE"
TIME_ZONE = "UTC"
USE_TZ = True


# =============================
# Static / Media
# =============================

STATIC_URL = "/static/"
STATIC_ROOT = os.getenv("STATIC_ROOT")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT")


# =============================
# Celery
# =============================

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

CELERY_TASK_TIME_LIMIT = 300
CELERY_TASK_SOFT_TIME_LIMIT = 270

CELERY_CACHE_BACKEND = 'default'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_PUBLISH_RETRY = True
CELERY_RESULT_EXTENDED = True

CELERY_TIMEZONE = "Europe/Berlin"
CELERY_ENABLE_UTC = True

CELERY_TASK_ROUTES = {
    "market.tasks.*": {
        "queue": "market",
    },
    "devices.tasks.*": {
        "queue": "aggregation",
    },
    "core.tasks.*": {
        "queue": "aggregation",
    },
    "integrations.tasks.*": {
        "queue": "telemetry",
    },
    "demo.tasks.*": {
        "queue": "demo",
    },
    "forecast.tasks.*": {
        "queue": "forecast",
    },
    "billing.tasks.*": {
        "queue": "critical",
    },
    "accounts.tasks.*": {
        "queue": "critical",
    },
}

CELERY_BEAT_SCHEDULE = {
    # ✅ Multi-Queue-Monitoring
    "health-checks": {
        "task": "operations.tasks.run_health_checks",
        "schedule": 300.0,
    },
    # Balance regelmäßig nachziehen
    "compute-balance": {
        "task": "billing.tasks.compute_balance_last_24h",
        "schedule": 300.0,
    },
    "allocate-user-balance": {
        "task": "billing.tasks.allocate_user_balance_last_24h",
        "schedule": crontab(minute="*/15"),
    },
    # ✅ DB Aggregation triggern
    "rollup-15min": {
        "task": "core.tasks.rollup_15min",
        "schedule": 60.0,
    },
    # ✅ Balance berechnen (dirty slots)
    "process-dirty-balance": {
        "task": "core.tasks.process_dirty_balance",
        "schedule": 60.0,
    },
    # ✅ Tibber Daten holen
    "tibber-sync": {
        "task": "integrations.tasks.sync_tibber",
        "schedule": 1800.0,
    },
    # ✅ Strompreise Day-Ahead Fenster (13:00 - 18:59 alle 15m + 00:05 Safety)
    "fetch-spot-prices-daily": {
        "task": "market.tasks.fetch_spot_prices_retry",
        "schedule": crontab(hour="0,13,14,15,16,17,18", minute="5,20,35,50"),
    },
    # ✅ MagicLogin CleanUp
    "cleanup_tokens": {
        "task": "accounts.tasks.cleanup_tokens",
        "schedule": crontab(hour=3, minute=0),
    },
    # ✅ MQTT Buffer
    "flush-mqtt-buffer": {
        "task": "integrations.tasks.flush_mqtt_buffer",
        "schedule": 5.0,  # alle 5 Sekunden
    },
    # ✅ 1m Aggregation
    "aggregate-1m": {
        "task": "devices.tasks.run_1m_aggregation",
        "schedule": 60.0,
    },
    # ✅ 5m Aggregation
    "aggregate-5m": {
        "task": "devices.tasks.run_5m_aggregation",
        "schedule": crontab(minute="*/5"),
    },
    # ✅ 15m Aggregation
    "aggregate-15m": {
        "task": "devices.tasks.run_15m_aggregation",
        "schedule": crontab(minute="*/15"),
    },
    # ✅ 1h Aggregation
    "aggregate-1h": {
        "task": "devices.tasks.run_1h_aggregation",
        "schedule": crontab(minute=0),
    },
    # ✅ Device purge
    "purge-pending-devices": {
        "task": "devices.tasks.purge_pending_devices",
        "schedule": crontab(hour="*/6"),
    },
    # ✅ Sync Demo Live Metrics
    "sync-demo-metrics": {
        "task": "demo.tasks.sync_demo_metrics",
        "schedule": 15.0,
    },
    # ✅ Sync Demo Device Metric cleanup
    "demo-cleanup": {
        "task": "demo.tasks.cleanup_demo",
        "schedule": 86400.0,
    },
    # ✅ Sync Demo Device delete
    "demo-device-sync": {
        "task": "demo.tasks.sync_demo_devices",
        "schedule": 86400.0,
    },
    # ✅ Sync Demo Device Config
    "demo-config-sync": {
        "task": "demo.tasks.sync_demo_configs",
        "schedule": 3600.0,
    },
    # ✅ Forecast Weather Update
    "update-forecasts-every-30-minutes": {
        "task": "forecast.tasks.update_all_forecasts",
        "schedule": crontab(minute="*/30"),
    },
    # ✅ Forecast Weather Data
    "fetch-weather-data": {
        "task": "forecast.tasks_weather.fetch_weather_data",
        "schedule": 60 * 30,
    },
    #  ✅ Forecast Weather Realtime Update
    "fetch-weather-observations": {
        "task": "forecast.tasks_weather_observations.fetch_weather_observations",
        "schedule": 60 * 15,
    },
    #  ✅ ML Forecast Training (nächtlich)
    "train-ml-forecast-models": {
        "task": "forecast.tasks.train_all_generator_ml_models",
        "schedule": crontab(hour=2, minute=30),
    },
}

# =============================
# Redis / Cache / Channels
# =============================

ASGI_APPLICATION = "backend.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.getenv("CHANNEL_LAYERS_URL")],
            "capacity": 1500,
            "expiry": 10,
        },
    },
    "energy": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },


}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL"),
    }
}


# =============================
# Logging
# =============================

DJANGO_LOG_LEVEL = "DEBUG" if DEBUG else "INFO"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["stdout"],
        "level": DJANGO_LOG_LEVEL,
    },
    # 🔥 HIER GEZIELT DIE LOGGERS FÜR DIE RUHE EINBAUEN:
    "loggers": {
        "matplotlib": {
            "handlers": ["stdout"],
            "level": "WARNING",  # Filtert das "findfont"-Geschnatter heraus
            "propagate": False,  # Verhindert das Weiterreichen an den root-logger
        },
        "PIL": {
            "handlers": ["stdout"],
            "level": "WARNING",  # Filtert die "STREAM"-Bildlogs heraus
            "propagate": False,
        },
    },
}


# =====================================
# MQTT
# =====================================
MQTT_INGEST_ENABLED = os.getenv("MQTT_INGEST_ENABLED", "False") == "True"
MQTT_AUTO_PROVISION = os.getenv("MQTT_AUTO_PROVISION", "False") == "True"
MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "h/+/+")
MQTT_QOS = int(os.getenv("MQTT_QOS", 1))
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "default-client")
MQTT_PROFILE = os.getenv("MQTT_PROFILE", "")

MQTT_ADMIN_USER = os.getenv("MQTT_ADMIN_USER")
MQTT_ADMIN_PASSWORD = os.getenv("MQTT_ADMIN_PASSWORD")
MQTT_CAFILE = os.getenv("MQTT_CAFILE")
MQTT_CTRL_PATH = os.getenv("MQTT_CTRL_PATH")


# =============================
# Sentry
# =============================

SENTRY_DSN = os.getenv("SENTRY_DSN")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        send_default_pii=False,
        traces_sample_rate=0.1,
    )
