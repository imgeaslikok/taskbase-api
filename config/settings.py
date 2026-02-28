import os
from datetime import timedelta
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent  # config/ -> project root

DJANGO_ENV = os.environ.get("DJANGO_ENV", "dev").lower()  # dev | test | prod

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-unsafe-key")

# Keep DEBUG explicit; allow env override, but also provide sane defaults by env.
if "DJANGO_DEBUG" in os.environ:
    DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"
else:
    DEBUG = DJANGO_ENV == "dev"

# ALLOWED_HOSTS: in dev allow everything unless explicitly set (simple DX).
if DJANGO_ENV == "dev" and "DJANGO_ALLOWED_HOSTS" not in os.environ:
    ALLOWED_HOSTS: list[str] = []
else:
    ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(
        ","
    )


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
    "apps.core",
    "apps.projects",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "api.common.middleware.RequestIdMiddleware",
    "api.common.middleware.AccessLogMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"


DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=60,
    )
}


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "auth_login": "10/min",
        "auth_refresh": "30/min",
    },
    "DEFAULT_PAGINATION_CLASS": "api.common.pagination.DefaultPageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "api.common.exceptions.core_exception_handler",
}

# Tests: avoid flaky throttling without disabling the mechanism entirely.
if DJANGO_ENV == "test":
    REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
        **REST_FRAMEWORK.get("DEFAULT_THROTTLE_RATES", {}),
        "auth_login": "10000/min",
        "auth_refresh": "10000/min",
    }

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "UPDATE_LAST_LOGIN": True,
}

SPECTACULAR_SETTINGS = {
    "TITLE": os.environ.get("API_TITLE", "TaskBase API"),
    "DESCRIPTION": os.environ.get(
        "API_DESCRIPTION", "Minimal, production-ready Task Management Project."
    ),
    "VERSION": os.environ.get("API_VERSION", "1.0.0"),
    "SERVE_INCLUDE_SCHEMA": False,
    "SECURITY": [{"bearerAuth": []}],
    "COMPONENT_SPLIT_REQUEST": True,
    "SECURITY_DEFINITIONS": {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    },
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {"()": "api.common.logging.RequestIdFilter"},
    },
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["request_id"],
            "formatter": "default",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "api": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        # Use env-aware namespace to avoid cross-env collisions (esp. during tests).
        "LOCATION": f"taskbase:{DJANGO_ENV}:default",
    }
}


# Test-only speedups
if DJANGO_ENV == "test":
    PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]
