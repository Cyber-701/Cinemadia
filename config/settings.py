import os
from pathlib import Path

# Agar dj-database-url o'rnatilgan bo'lsa
try:
    from dj_database_url import parse as db_url
except ImportError:
    db_url = None

# Project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DEBUG", "0") == "1"

# Hosts
BASE_ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1,cinemadia-com-1.onrender.com,cinemadia.com"
    ).split(",")
    if host.strip()
]

# Ngrok tunnel domenlari (development uchun)
NGROK_WILDCARDS = [".ngrok-free.app", ".ngrok-free.dev", ".ngrok.io"]
ALLOWED_HOSTS = BASE_ALLOWED_HOSTS + [h for h in NGROK_WILDCARDS if h not in BASE_ALLOWED_HOSTS]

CSRF_TRUSTED_ORIGINS = [
    f"https://{host}"
    for host in BASE_ALLOWED_HOSTS
    if host not in ("localhost", "127.0.0.1")
]
CSRF_TRUSTED_ORIGINS += [
    "https://*.ngrok-free.app",
    "https://*.ngrok-free.dev",
    "https://*.ngrok.io",
]

# Ngrok HTTPS proksi orqasida to'g'ri scheme aniqlash
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Database
database_url = os.environ.get("DATABASE_URL")
if db_url and database_url:
    DATABASES = {
        "default": db_url(database_url, conn_max_age=600),
    }
else:
    # Fallback to SQLite
    DATABASES = {
        "default": {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'crispy_forms',
    'crispy_bootstrap5',

    'cinemadia',  # sizning app nomingiz
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Default auto field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
