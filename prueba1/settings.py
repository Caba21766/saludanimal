"""
Django settings for prueba1 (producción)
Docs: https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from django.urls import reverse_lazy
from dotenv import load_dotenv  # type: ignore

# =========================================================
# Paths & .env
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")  # lee /opt/vete/.env

def csv_env(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [x.strip() for x in raw.split(",") if x.strip()]

def env_bool(name, default=False):
    return str(os.getenv(name, str(default))).strip().lower() in {"1", "true", "yes", "on"}

def env_int(name, default):
    try:
        return int(str(os.getenv(name, "")).strip())
    except (TypeError, ValueError):
        return default

# =========================================================
# Core
# =========================================================
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DEBUG", "False").strip().lower() == "true"

ALLOWED_HOSTS = csv_env("ALLOWED_HOSTS")
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]

# URLs de auth
LOGIN_URL = reverse_lazy("apps.blog_auth:iniciar_sesion")
LOGIN_REDIRECT_URL = reverse_lazy("index")
LOGOUT_REDIRECT_URL = reverse_lazy("index")

# CSRF trusted origins
csrf_from_env = csv_env("CSRF_TRUSTED_ORIGINS")
if csrf_from_env:
    CSRF_TRUSTED_ORIGINS = csrf_from_env
else:
    _csrf = []
    for h in ALLOWED_HOSTS:
        _csrf.append(f"http://{h}")
        _csrf.append(f"https://{h}")
    CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(_csrf))

# =========================================================
# n8n Magic Link
# =========================================================
N8N_API_KEY = os.environ.get("N8N_API_KEY", "")

# =========================================================
# Apps
# =========================================================
AUTHENTICATION_BACKENDS = [
    "apps.blog_auth.backends.DNIBackend",
    "django.contrib.auth.backends.ModelBackend",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "widget_tweaks",
    "django.contrib.sitemaps",

    # Apps propias
    "apps.backup",
    "apps.modulo1",
    "apps.opiniones",
    "apps.blog_auth",
    "apps.CarritoApp",
    "apps.libros",
    "apps.mascota",
    "prueba1",
    "apps.patch_user",
    "apps.turnos.apps.TurnosConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "prueba1.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "utils.context_processor.categorias_context",
            ],
        },
    },
]

WSGI_APPLICATION = "prueba1.wsgi.application"


# =========================================================
# Base de datos (MySQL) - compat mysqlclient (MySQLdb)
# =========================================================

_db_options = {}

DB_SSL_MODE = os.getenv("DB_SSL_MODE", "DISABLED").strip().upper()
ssl_ca = os.getenv("DB_SSL_CA", "").strip()

# Si la DB es local, NO usamos SSL (evita problemas de cert)
db_host = (os.getenv("DB_HOST") or "").strip()
is_local_db = db_host in {"127.0.0.1", "localhost"}

if not is_local_db:
    # Si NO es local, recién ahí evaluamos SSL
    if ssl_ca and DB_SSL_MODE not in {"DISABLED", "OFF", "0", "FALSE", "NO"}:
        _db_options["ssl"] = {"ca": ssl_ca}
    elif DB_SSL_MODE in {"REQUIRED", "ON", "TRUE", "1"}:
        # SSL sin verificación (cifra pero no valida cert)
        _db_options["ssl"] = {}
else:
    # Fuerzo no-SSL para local
    _db_options = {}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": db_host,
        "PORT": os.getenv("DB_PORT", "3306"),
        "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "120")),
        "OPTIONS": _db_options,
    }
}

# =========================================================
# Passwords
# =========================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =========================================================
# I18N / TZ
# =========================================================
LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

# =========================================================
# Static & Media (Nginx sirve estos paths)
# =========================================================
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

_static_dir = BASE_DIR / "static"
STATICFILES_DIRS = [_static_dir] if _static_dir.exists() else []

STATIC_ROOT = Path("/var/www/sitioscom/static")
MEDIA_ROOT = Path("/var/www/sitioscom/media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================================================
# Seguridad para producción (activar con HTTPS)
# =========================================================
if not DEBUG:
    # Detrás de Nginx / Cloudflare
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True

    # Redirección a HTTPS (si Cloudflare está en Full/Strict y Nginx acepta)
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)

    # Cookies seguras
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", True)
    CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", True)
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    CSRF_COOKIE_SAMESITE = os.getenv("CSRF_COOKIE_SAMESITE", "Lax")

    # HSTS
    _hsts = os.getenv("SECURE_HSTS_SECONDS", "31536000")
    SECURE_HSTS_SECONDS = 0 if str(_hsts).strip().lower() in {"false", "0", ""} else env_int("SECURE_HSTS_SECONDS", 31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
    SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", True)

    # Headers extra
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

# =========================================================
# Cache (locmem por defecto)
# =========================================================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "prueba1-locmem",
        "TIMEOUT": int(os.getenv("CACHE_TIMEOUT", "300")),
    }
}

# =========================================================
# Email
# =========================================================
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587") or "587")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").strip().lower() == "true"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@sitioscom.com.ar")

# =========================================================
# Logging
# =========================================================
LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": True},
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": True},
    },
}

# =========================================================
# Mercado Pago
# =========================================================
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN", "")
# ✅ NO volver a redefinir ALLOWED_HOSTS ni CSRF_TRUSTED_ORIGINS acá