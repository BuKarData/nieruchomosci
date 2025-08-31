import os
from pathlib import Path
import dj_database_url

# Ścieżki
BASE_DIR = Path(__file__).resolve().parent.parent

#  Bezpieczny Secret Key
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "super-secret-key")

# Debug
DEBUG = os.environ.get("DEBUG", "True") == "True"

#  Dozwolone hosty (na Railway najlepiej *)
ALLOWED_HOSTS = ["bzbud.pl", "www.bzbud.pl", "0s2qosca.up.railway.app", 'web-production-48d26.up.railway.app']


CSRF_TRUSTED_ORIGINS = [
    "https://www.bzbud.pl",
    "https://bzbud.pl",
    "https://web-production-48d26.up.railway.app",  # opcjonalnie dla testów
]

# Aplikacje
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
     "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "oferty",
    "rest_framework",
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # statyczne pliki
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

#  URL conf i WSGI
ROOT_URLCONF = "nieruchomosci.urls"
WSGI_APPLICATION = "nieruchomosci.wsgi.application"

# Zdjecia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Szablony
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
            ],
        },
    }
]

# Baza danych
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_PUBLIC_URL'),
        conn_max_age=600,
    )
}

# Walidatory haseł
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

#  Międzynarodowe ustawienia
LANGUAGE_CODE = "pl-pl"
TIME_ZONE = "Europe/Warsaw"
USE_I18N = True
USE_TZ = True

#  Pliki statyczne
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

#  Pliki media (jeżeli używasz)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

#  Domyślne auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
