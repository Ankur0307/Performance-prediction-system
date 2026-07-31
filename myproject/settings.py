"""
Django settings for myproject project.
Supports both local development and Vercel production deployment.
"""

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

# Read SECRET_KEY from environment in production; fall back for local dev.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure--=@7)k1mur)&xgmdey&ay(v$1cjssmx@6*(4ud1)_^8si0lx5)'
)

# DEBUG is False in production (Vercel sets VERCEL=1 automatically).
DEBUG = os.environ.get('DEBUG', 'False') != 'False'

ALLOWED_HOSTS = [
    '192.168.1.11',
    'localhost',
    '127.0.0.1',
    # Vercel deployment domains
    '.vercel.app',
    # Render.com deployment domains
    '.onrender.com',
]

# Allow the VERCEL_URL env var to be added automatically
VERCEL_URL = os.environ.get('VERCEL_URL')
if VERCEL_URL:
    ALLOWED_HOSTS.append(VERCEL_URL)


# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp.apps.MyappConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must come right after SecurityMiddleware to serve static files
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

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

WSGI_APPLICATION = 'myproject.wsgi.application'


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# In production (Vercel) set DATABASE_URL env variable to a PostgreSQL URL.
# Falls back to local SQLite for development.

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static files — WhiteNoise serves them directly from Django on Vercel
# ---------------------------------------------------------------------------

STATIC_URL = '/static/'

# Directory where collectstatic gathers all static files
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Extra locations collectstatic should look for static files
STATICFILES_DIRS = [
    BASE_DIR / 'myapp' / 'static',
]

# WhiteNoise compressed manifest storage for production caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ---------------------------------------------------------------------------
# ML Model path
# ---------------------------------------------------------------------------

ML_MODEL_PATH = BASE_DIR / 'random_forest_model.pkl'


# ---------------------------------------------------------------------------
# Default primary key field type
# ---------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
