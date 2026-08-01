import os
from pathlib import Path
from decouple import config

# ========================
# Core Django Configuration
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

def parse_bool_config(name, default=False):
    try:
        return config(name, default=default, cast=bool)
    except ValueError:
        return default

DEBUG = parse_bool_config('DEBUG', default=False)

ALLOWED_HOSTS = [
    "eunccu.org",
    "www.eunccu.org",
    "127.0.0.1",
    "127.0.0.1:8000",
    "localhost",
    
]

ROOT_URLCONF = 'union.urls'
WSGI_APPLICATION = 'union.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'website:login'
LOGIN_REDIRECT_URL = '/'

# =============
# Applications
# =============
INSTALLED_APPS = [
    'django_ckeditor_5',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'widget_tweaks',
    'bootstrap3',
    'django_forms_bootstrap',
    'django_extensions',

    # Local
    'website',
    'auth_utils.apps.AuthUtilsConfig',
]

# =============
# Middleware
# =============
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # --- Onboarding redirects incomplete profiles to complete theiregistration-------
    'website.middleware.ProfileCompletionMiddleware',
]

# -----
# Security Settings

USE_HTTPS = config('USE_HTTPS', default=False, cast=bool)

if USE_HTTPS:
    # HTTPS is enabled
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
else:
    # HTTP only
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    # HSTS should not be enabled when not using HTTPS
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_PRELOAD = False
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False

# These work with both HTTP and HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = 'DENY'

## Note: Do not override USE_HTTPS-derived settings below this line.

# =============
# Database
# =============

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME', default='postgres'),
        'USER': config('DATABASE_USER', default='postgres'),
        'PASSWORD': config('DATABASE_PASSWORD', default=''),
        'HOST': config('DATABASE_HOST', default='localhost'),
        'PORT': config('DATABASE_PORT', default=5432, cast=int),
    }
}

# =============
# Templates
# =============
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# =============
# Internationalization
# =============
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True



# Static & Media
# =============
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG

# =============
# Email Settings
# =============
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'eunccu.org'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = f'Egerton University Njoro Campus Christian Union <{EMAIL_HOST_USER}>'
NOTIFICATION_DELAY_SECONDS = config('NOTIFICATION_DELAY_SECONDS', default=60, cast=int)

# =============
# YouTube API
# =============
YOUTUBE_API_KEY = config('YOUTUBE_API_KEY', default='')
YOUTUBE_PLAYLIST_ID = config('YOUTUBE_PLAYLIST_ID', default='')
YOUTUBE_REGION_CODE = config('YOUTUBE_REGION_CODE', default='KE')

# Google Drive Integration
GOOGLE_DRIVE_ENABLED = config('GOOGLE_DRIVE_ENABLED', default=False, cast=bool)
GOOGLE_DRIVE_FOLDER_ID = config('GOOGLE_DRIVE_FOLDER_ID', default='')
GOOGLE_SERVICE_ACCOUNT_FILE = config('GOOGLE_SERVICE_ACCOUNT_FILE', default='')

# =============
# Custom User
# =============
AUTH_USER_MODEL = 'website.CustomUser'

# =============
# Onboarding
# =============
# Default temporary password assigned to newly onboarded users.
# Change this value in your .env or here before deployment.
DEFAULT_TEMP_PASSWORD = config('DEFAULT_TEMP_PASSWORD', default='student')

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'website.backends.EmailAuthBackend',
    'website.backends.CustomUserAuthBackend',
]

# =============
# Upload Limits
# =============
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024

# =============
# Session
# =============
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 600
SESSION_SAVE_EVERY_REQUEST = True

# =============
# Cache
# =============

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 4 * 60 * 60,
    }
}

# =============
# Logging
# =============
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# CKEditor 5
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', '|',
            'bulletedList', 'numberedList', 'blockQuote', '|',
            'link', 'imageUpload', '|',
            'undo', 'redo'
        ],
    },
}
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
X_FRAME_OPTIONS = 'SAMEORIGIN'

# 
JAZZMIN_SETTINGS = {
    "site_title": "EUNCCU Admin",
    "site_header": "EUNCCU",
    "welcome_sign": "Welcome to the EUNCCU Management Portal",
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "website.Event"},
        {"model": "website.Devotion"},
        {"model": "website.SemesterThemes"},
        {"model": "website.Contact"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "website.Event": "fas fa-calendar-alt",
        "website.Devotion": "fas fa-bible",
        "website.Leader": "fas fa-user-tie",
        "website.Contact": "fas fa-envelope",
    },
}
