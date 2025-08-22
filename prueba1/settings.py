"""


For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
from django.urls import reverse_lazy
from dotenv import load_dotenv # type: ignore

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
# ------ LOGIN -----

LOGIN_URL = reverse_lazy('apps.blog_auth:iniciar_sesion')
LOGIN_REDIRECT_URL = reverse_lazy('index')
LOGOUT_REDIRECT_URL = reverse_lazy('index')

# -------------------------------------------------------------------------------------
ENV_SECRET_KEY = os.getenv("SECRET_KEY")

SECRET_KEY = os.getenv("SECRET_KEY")
# -------------------------------------------------------------------------------------

DEBUG = True

# -------------------------------------------------------------------------------------

ALLOWED_HOSTS = ['*']

# -------------------------------------------------------------------------------------

AUTHENTICATION_BACKENDS = [
    "apps.blog_auth.backends.DNIBackend",    # <— nuestro backend por DNI
    "django.contrib.auth.backends.ModelBackend",
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'widget_tweaks',
    
    # Custom apps
    'apps.backup',
    'apps.modulo1',
    'apps.opiniones',
    'apps.blog_auth',
    'apps.CarritoApp',
    'apps.libros', 
    'apps.mascota',
    'prueba1',
    'apps.patch_user'
    
]
# -------------------------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
# -------------------------------------------------------------------------------------
ROOT_URLCONF = "prueba1.urls"
# -------------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [ BASE_DIR / "templates" ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # context_processors_customizados
                "utils.context_processor.categorias_context"
            ],
        },
    },
]
# -------------------------------------------------------------------------------------
WSGI_APPLICATION = "prueba1.wsgi.application"
# -------------------------------------------------------------------------------------
#NAME_DB = os.getenv("NAME_DB")
#USER_DB = os.getenv("USER_MYSQL")
#PASSWORD_DB =  os.getenv("PASSWORD_MYSQL")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "Vete2025",
        "USER": "root",
        "PASSWORD": "Root",
        "HOST": "localhost",  # Host de la base de datos
        "PORT": '3306'
    }
}
# -------------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# -------------------------------------------------------------------------------------

LANGUAGE_CODE = "es-ar"

TIME_ZONE = "America/Argentina/Buenos_Aires"

USE_I18N = True

USE_TZ = True

# -------------------------------------------------------------------------------------

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'


MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# -------------------------------------------------------------------------------------
# 🔹 Configurar Mercado Pago

# -------------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")