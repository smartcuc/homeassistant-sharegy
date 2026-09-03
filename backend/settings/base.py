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
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration



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
FRONTEND_BASE_URL = FRONTEND_URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TRACKING_BASE_URL = os.getenv("TRACKING_BASE_URL", BACKEND_URL)


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
        "accounts.auth_api_key.APIKeyOrTokenAuthentication",
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

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 465))

# Intelligente SSL/TLS Erkennung mit Env-Override
_default_ssl = "True" if EMAIL_PORT == 465 else "False"
_default_tls = "True" if EMAIL_PORT == 587 else "False"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", _default_ssl).lower() == "true"
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", _default_tls).lower() == "true"
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", 10))

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
    "alerts",
    "operations",
    "tracking",
    "support_desk",
    "notifications",
    "providers.opentelemetry",
]



# =============================
# Web-Push (VAPID) / Notifications
# =============================

VAPID_PUBLIC_KEY = os.getenv(
    "VAPID_PUBLIC_KEY",
    "BEvm41zaXEwSGOLlCWheNkipNaW-WIx8-ETiYm2DrmghxWarI87KLGltqY_kfMnnyasIt5Oh4oU3leT9ldY2feM"
)
VAPID_PRIVATE_KEY = os.getenv(
    "VAPID_PRIVATE_KEY",
    "-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgPYhlwFNIU1yiu7DO\nuopVIiWWBjC/FxEFVvJjOqa3YimhRANCAARL5uNc2lxMEhji5QloXjZIqTWlvliM\nfPhE4mJtg65oIcVmqyPOyixpbamP5HzJ58mrCLeToeKFN5Xk/ZXWNn3j\n-----END PRIVATE KEY-----"
)
VAPID_ADMIN_EMAIL = os.getenv(
    "VAPID_ADMIN_EMAIL",
    "mailto:support@sharegy.cloud"
)


# =============================
# ☀️ Sungrow iSolarCloud OAuth 2.0
# =============================
SUNGROW_APPKEY = os.getenv("SUNGROW_APPKEY", "")
SUNGROW_APP_SECRET = os.getenv("SUNGROW_APP_SECRET", "")
SUNGROW_GATEWAY_URL = os.getenv("SUNGROW_GATEWAY_URL", "https://gateway.isolarcloud.eu")
SUNGROW_REDIRECT_URL = os.getenv("SUNGROW_REDIRECT_URL", "https://sharegy.de/api/v1/integrations/sungrow/callback")
SUNGROW_RSA_PUBLIC_KEY = os.getenv("SUNGROW_RSA_PUBLIC_KEY", "")



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
        "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", 60)),
        "CONN_HEALTH_CHECKS": True,
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

# Standard-Queue für alle nicht explizit gerouteten Tasks
CELERY_TASK_DEFAULT_QUEUE = "analytics"
CELERY_TASK_DEFAULT_EXCHANGE = "analytics"
CELERY_TASK_DEFAULT_ROUTING_KEY = "analytics"

# ==============================================================================
# 4-STUFEN CELERY TASK ROUTING ARCHITEKTUR
# 1. fiscal:     OBIS-Zählerdaten, Lastgänge, Abrechnung & Billing (Höchste Prio)
# 2. realtime:   MQTT Ingest-Puffer, Gerätesteuerbefehle & System-Health
# 3. analytics:  1m/5m/15m/1h Aggregationen, Spotpreise, Tibber, PV/Last-Forecasts
# 4. background: Scikit-Learn KI-Training, 8.7MB Wetter-Bulk, Retention & Purge
# ==============================================================================
CELERY_TASK_ROUTES = {
    # 💶 1. FISCAL & BILLING (Prio 1 - Höchste Integrität & Eichrecht)
    "core.tasks.*": {"queue": "fiscal"},
    "billing.tasks.*": {"queue": "fiscal"},
    "accounts.tasks.*": {"queue": "fiscal"},

    # ⚡ 2. EMS REALTIME & CONTROL (Prio 2 - Schnelle Reaktionszeit)
    "integrations.tasks.flush_mqtt_buffer": {"queue": "realtime"},
    "integrations.tasks.process_inbound_webhook_event": {"queue": "realtime"},
    "energy.tasks.*": {"queue": "realtime"},
    "operations.tasks.*": {"queue": "realtime"},

    # 💤 4. BACKGROUND & KI (Prio 4 - Schwere Batch-Jobs & Retention)
    "forecast.tasks_weather_observations.*": {"queue": "background"},
    "forecast.tasks.train_all_generator_ml_models": {"queue": "background"},
    "demo.tasks.cleanup_demo": {"queue": "background"},
    "devices.tasks.purge_pending_devices": {"queue": "background"},

    # 📊 3. EMS ANALYTICS & MARKT (Prio 3 - Standard)
    "devices.tasks.*": {"queue": "analytics"},
    "market.tasks.*": {"queue": "analytics"},
    "market.tasks_analysis.*": {"queue": "analytics"},
    "forecast.tasks.*": {"queue": "analytics"},
    "forecast.tasks_weather.*": {"queue": "analytics"},
    "integrations.tasks.*": {"queue": "analytics"},
    "demo.tasks.*": {"queue": "analytics"},
}

CELERY_BEAT_SCHEDULE = {
    # ✅ Multi-Queue-Monitoring (realtime)
    "health-checks": {
        "task": "operations.tasks.run_health_checks",
        "schedule": 300.0,
    },
    # 💶 Balance regelmäßig nachziehen (fiscal)
    "compute-balance": {
        "task": "billing.tasks.compute_balance_last_24h",
        "schedule": 300.0,
    },
    # 💶 Mieter- & Prosumer-Abrechnungsslots (fiscal)
    "allocate-user-balance": {
        "task": "billing.tasks.allocate_user_balance_last_24h",
        "schedule": crontab(minute="*/15"),
    },
    # 💶 Wöchentlicher 30-Tage Fiskal-Abgleich für extreme Offline-Zeiten (fiscal)
    "reconcile-balance-30d": {
        "task": "billing.tasks.reconcile_balance_last_30d",
        "schedule": crontab(hour=3, minute=0, day_of_week="sunday"),
    },
    # 💶 OBIS Zähler-Rollup auf DB-Ebene (fiscal)
    "rollup-15min": {
        "task": "core.tasks.rollup_15min",
        "schedule": 60.0,
    },
    # 💶 Dirty Balance berechnen auf DB-Ebene (fiscal)
    "process-dirty-balance": {
        "task": "core.tasks.process_dirty_balance",
        "schedule": 60.0,
    },
    # ⚡ MQTT Buffer Ingest (realtime)
    "flush-mqtt-buffer": {
        "task": "integrations.tasks.flush_mqtt_buffer",
        "schedule": 5.0,  # alle 5 Sekunden
    },
    # ☁️ Zyklisches Polling für Cloud-Wechselrichter (Sungrow, Kostal, SolarEdge, etc.)
    "poll-cloud-integrations": {
        "task": "devices.poll_cloud_integrations",
        "schedule": 60.0,  # alle 60 Sekunden
    },

    # 📊 1m Aggregation (analytics)
    "aggregate-1m": {
        "task": "devices.tasks.run_1m_aggregation",
        "schedule": 60.0,
    },
    # 📊 5m Aggregation (analytics)
    "aggregate-5m": {
        "task": "devices.tasks.run_5m_aggregation",
        "schedule": crontab(minute="*/5"),
    },
    # 📊 15m Aggregation (analytics)
    "aggregate-15m": {
        "task": "devices.tasks.run_15m_aggregation",
        "schedule": crontab(minute="*/15"),
    },
    # 📊 1h Aggregation (analytics)
    "aggregate-1h": {
        "task": "devices.tasks.run_1h_aggregation",
        "schedule": crontab(minute=0),
    },
    # 📊 Tibber Daten holen (analytics)
    "tibber-sync": {
        "task": "integrations.tasks.sync_tibber",
        "schedule": 1800.0,
    },
    # 📊 Strompreise Day-Ahead Fenster (analytics)
    "fetch-spot-prices-daily": {
        "task": "market.tasks.fetch_spot_prices_retry",
        "schedule": crontab(hour="0,13,14,15,16,17,18", minute="5,20,35,50"),
    },
    # 📊 Tägliche Strompreis-Analyse & Zeitfenster-Ranking (analytics)
    "compute-daily-spot-summary": {
        "task": "market.tasks_analysis.compute_daily_spot_summary",
        "schedule": crontab(hour="0,14", minute=5),
    },
    # 📊 Forecast Weather Update (analytics)
    "update-forecasts-every-30-minutes": {
        "task": "forecast.tasks.update_all_forecasts",
        "schedule": crontab(minute="*/30"),
    },
    # 📊 Forecast Weather Data Open-Meteo (analytics)
    "fetch-weather-data": {
        "task": "forecast.tasks_weather.fetch_weather_data",
        "schedule": 60 * 30,
    },
    # 📊 Autonome Demo Live-Simulation (analytics)
    "sync-demo-metrics": {
        "task": "demo.tasks.sync_demo_metrics",
        "schedule": 15.0,
    },
    # 💤 Forecast Weather Realtime Bulk-Observations Sensor.Community (background)
    "fetch-weather-observations": {
        "task": "forecast.tasks_weather_observations.fetch_weather_observations",
        "schedule": 60 * 15,
    },
    # 💤 ML Forecast Training nächtlich (background)
    "train-ml-forecast-models": {
        "task": "forecast.tasks.train_all_generator_ml_models",
        "schedule": crontab(hour=2, minute=30),
    },
    # 💤 MagicLogin CleanUp (fiscal/background)
    "cleanup_tokens": {
        "task": "accounts.tasks.cleanup_tokens",
        "schedule": crontab(hour=3, minute=0),
    },
    # 💤 Device purge (background)
    "purge-pending-devices": {
        "task": "devices.tasks.purge_pending_devices",
        "schedule": crontab(hour="*/6"),
    },
    # 💤 Tägliche Demo-Metriken Bereinigung (background)
    "demo-cleanup": {
        "task": "demo.tasks.cleanup_demo",
        "schedule": crontab(hour=3, minute=0),
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

SENTRY_DSN = os.getenv("SENTRY_DSN", "https://3fba9b14f3105d8ea0b18b1719a265bd@o4511998045650944.ingest.de.sentry.io/4511998083006544")
SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "production")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        environment=SENTRY_ENVIRONMENT,
        release="sharegy-backend@3.2.0",
        send_default_pii=False,
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
    )


# =============================
# 💳 STRIPE PAYMENTS & SANDBOX CONFIG
# =============================
STRIPE_SECRET_KEY = os.getenv("STRIPE_TEST_SECRET_KEY", os.getenv("STRIPE_SECRET_KEY", "")).strip()
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_TEST_PUBLIC_KEY", os.getenv("STRIPE_PUBLIC_KEY", "")).strip()
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()
STRIPE_SANDBOX_MODE = os.getenv("STRIPE_SANDBOX_MODE", "True").lower() in ("true", "1", "yes")

# Optional: Explizite Stripe Price-IDs für wiederkehrende Pläne (falls in Stripe Dashboard angelegt)
STRIPE_PRICE_IDS = {
    "pro_monthly": os.getenv("STRIPE_PRICE_PRO_MONTHLY", ""),
    "pro_yearly": os.getenv("STRIPE_PRICE_PRO_YEARLY", ""),
    "landlord_monthly": os.getenv("STRIPE_PRICE_LANDLORD_MONTHLY", ""),
    "landlord_yearly": os.getenv("STRIPE_PRICE_LANDLORD_YEARLY", ""),
}

