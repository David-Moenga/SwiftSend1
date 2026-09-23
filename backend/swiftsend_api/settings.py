from datetime import timedelta
import os
from pathlib import Path
from urllib.parse import urlsplit

import dj_database_url
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def clean_host(value):
    cleaned = (value or "").strip()
    if not cleaned:
        return ""

    parsed = urlsplit(
        cleaned if "://" in cleaned else f"//{cleaned}"
    )
    hostname = parsed.hostname or cleaned

    return hostname.strip("[]/")


# -------------------------------------------------------------------
# Environment
# -------------------------------------------------------------------

ENVIRONMENT = os.environ.get("DJANGO_ENV", "development").lower()

# Render sets the RENDER environment variable.
IS_RENDER = bool(os.environ.get("RENDER"))

IS_PRODUCTION = (
    ENVIRONMENT == "production"
    or IS_RENDER
)

DEBUG = not IS_PRODUCTION


# -------------------------------------------------------------------
# Secret Key
# -------------------------------------------------------------------

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    if IS_PRODUCTION:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY must be set outside development."
        )

    SECRET_KEY = "django-insecure-development-key-not-for-production"


# -------------------------------------------------------------------
# Allowed Hosts
# -------------------------------------------------------------------

DEFAULT_ALLOWED_HOSTS = "localhost,127.0.0.1"

configured_hosts = [
    host
    for host in (
        clean_host(value)
        for value in os.environ.get(
            "DJANGO_ALLOWED_HOSTS",
            DEFAULT_ALLOWED_HOSTS,
        ).split(",")
    )
    if host
]


if IS_PRODUCTION:
    render_host = (
        os.environ.get("RENDER_EXTERNAL_HOSTNAME")
        or os.environ.get("RENDER_HOSTNAME")
    )

    if render_host:
        configured_hosts.append(clean_host(render_host))

    # Allow Render subdomains.
    configured_hosts.append(".onrender.com")


ALLOWED_HOSTS = list(dict.fromkeys(configured_hosts))


# -------------------------------------------------------------------
# Installed Applications
# -------------------------------------------------------------------

INSTALLED_APPS = [
    "corsheaders",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",

    "accounts",
    "transfers",
]


# -------------------------------------------------------------------
# Middleware
# -------------------------------------------------------------------

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# -------------------------------------------------------------------
# URL / Application Configuration
# -------------------------------------------------------------------

ROOT_URLCONF = "swiftsend_api.urls"

WSGI_APPLICATION = "swiftsend_api.wsgi.application"
ASGI_APPLICATION = "swiftsend_api.asgi.application"


# -------------------------------------------------------------------
# Templates
# -------------------------------------------------------------------

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


# -------------------------------------------------------------------
# Database
# -------------------------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# -------------------------------------------------------------------
# Password Validation
# -------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]


# -------------------------------------------------------------------
# Internationalization
# -------------------------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# -------------------------------------------------------------------
# Static Files
# -------------------------------------------------------------------

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# -------------------------------------------------------------------
# Django REST Framework
# -------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}


# -------------------------------------------------------------------
# JWT
# -------------------------------------------------------------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),

    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "ROTATE_REFRESH_TOKENS": True,

    "BLACKLIST_AFTER_ROTATION": True,

    "AUTH_HEADER_TYPES": ("Bearer",),
}


# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]


# -------------------------------------------------------------------
# CSRF
# -------------------------------------------------------------------

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]


# -------------------------------------------------------------------
# Production Security
# -------------------------------------------------------------------

if IS_PRODUCTION:
    SECURE_SSL_REDIRECT = True

    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 31_536_000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True

