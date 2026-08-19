import os
from pathlib import Path
from decouple import config

# ========================
# Core Django Configuration
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent



def get_config_value(name, default=None, cast=None):
    config_kwargs = {'default': default}
    if cast is not None:
        config_kwargs['cast'] = cast

    value = config(name, **config_kwargs)
    if isinstance(value, str):
        value = value.strip()
    return value


def get_config_list(name, default=None, separator=','):
    value = get_config_value(name, default=default)
    if value is None:
        return []
    return [item.strip() for item in value.split(separator) if item.strip()]


SECRET_KEY = get_config_value('SECRET_KEY', default='django-insecure-dev-secret-key-change-me')


def parse_bool_config(name, default=False):
    try:
        return get_config_value(name, default=default, cast=bool)
    except ValueError:
        return default

ENVIRONMENT = get_config_value('ENVIRONMENT', default='development').lower()
DEBUG = parse_bool_config('DEBUG', default=(ENVIRONMENT != 'production'))

default_allowed_hosts = 'localhost,127.0.0.1,127.0.0.1:8000' if ENVIRONMENT != 'production' else 'eunccu.org,www.eunccu.org'
ALLOWED_HOSTS = get_config_list(
    'ALLOWED_HOSTS',
    default=default_allowed_hosts,
)

CSRF_TRUSTED_ORIGINS = get_config_list(
    'CSRF_TRUSTED_ORIGINS',
    default='https://eunccu.org,https://www.eunccu.org' if ENVIRONMENT == 'production' else 'http://localhost:8000,http://127.0.0.1:8000',
)

ROOT_URLCONF = 'union.urls'
WSGI_APPLICATION = 'union.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'website:login'
LOGIN_REDIRECT_URL = '/'

# =============
# Applications
# =============
INSTALLED_APPS = [
    'jazzmin',  # Admin interface
    'django_ckeditor_5',  # Rich text editor
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'widget_tweaks',
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

USE_HTTPS = get_config_value('USE_HTTPS', default=(ENVIRONMENT == 'production'), cast=bool)

if DEBUG:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_PRELOAD = False
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
else:
    SECURE_SSL_REDIRECT = parse_bool_config('SECURE_SSL_REDIRECT', default=USE_HTTPS)
    SESSION_COOKIE_SECURE = parse_bool_config('SESSION_COOKIE_SECURE', default=USE_HTTPS)
    CSRF_COOKIE_SECURE = parse_bool_config('CSRF_COOKIE_SECURE', default=USE_HTTPS)
    SECURE_HSTS_SECONDS = get_config_value('SECURE_HSTS_SECONDS', default=31536000, cast=int) if USE_HTTPS else 0
    SECURE_HSTS_PRELOAD = parse_bool_config('SECURE_HSTS_PRELOAD', default=USE_HTTPS)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = parse_bool_config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=USE_HTTPS)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# These work with both HTTP and HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = 'DENY'

## Note: Do not override USE_HTTPS-derived settings below this line.

# =============
# Database
# =============
if DEBUG:

       DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.sqlite3',
               'NAME': BASE_DIR / 'db.sqlite3',
           }
       }


else:
    pass
#DATABASE_ENGINE = 'mysql'

#DATABASES = {
    #'default': {
        #'ENGINE': 'django.db.backends.mysql',
        #'NAME': get_config_value('DATABASE_NAME', default='django_db'),
        #'USER': get_config_value('DATABASE_USER', default='root'),
        #'PASSWORD': get_config_value('DATABASE_PASSWORD', default=''),
        #'HOST': get_config_value('DATABASE_HOST', default='localhost'),
        #'PORT': get_config_value('DATABASE_PORT', default=3306, cast=int),
    #}
#}

# MySQL options
#if True:
   # DATABASES['default']['OPTIONS'] = {
        #'init_command': "SET sql_mode='STRICT_TRANS_TABLES', innodb_strict_mode=1",
        #'charset': 'utf8mb4',
    #}

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

# =============
# Caching
# =============
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Static & Media
# =============
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

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
EMAIL_HOST_USER = get_config_value('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_config_value('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = f'Egerton University Njoro Campus Christian Union <{EMAIL_HOST_USER}>'
NOTIFICATION_DELAY_SECONDS = get_config_value('NOTIFICATION_DELAY_SECONDS', default=60, cast=int)

# The public site root used to build absolute links in out-of-request contexts.
SITE_URL = get_config_value('SITE_URL', default='https://eunccu.org')

# =============
# YouTube API
# =============
YOUTUBE_API_KEY = get_config_value('YOUTUBE_API_KEY', default='')
YOUTUBE_PLAYLIST_ID = get_config_value('YOUTUBE_PLAYLIST_ID', default='')
YOUTUBE_REGION_CODE = get_config_value('YOUTUBE_REGION_CODE', default='KE')

# Google Drive Integration
GOOGLE_DRIVE_ENABLED = get_config_value('GOOGLE_DRIVE_ENABLED', default=False, cast=bool)
GOOGLE_DRIVE_FOLDER_ID = get_config_value('GOOGLE_DRIVE_FOLDER_ID', default='')
GOOGLE_DRIVE_BACKUP_FOLDER_ID = get_config_value('GOOGLE_DRIVE_BACKUP_FOLDER_ID', default='')
GOOGLE_DRIVE_AUTH_METHOD = get_config_value('GOOGLE_DRIVE_AUTH_METHOD', default='service_account')
GOOGLE_DRIVE_OAUTH_CLIENT_SECRETS_FILE = get_config_value('GOOGLE_DRIVE_OAUTH_CLIENT_SECRETS_FILE', default='')
GOOGLE_DRIVE_OAUTH_TOKEN_FILE = get_config_value('GOOGLE_DRIVE_OAUTH_TOKEN_FILE', default='google_drive_token.json')
GOOGLE_SERVICE_ACCOUNT_FILE = get_config_value('GOOGLE_SERVICE_ACCOUNT_FILE', default='')
GOOGLE_BACKUP_DRIVE_AUTH_METHOD = get_config_value('GOOGLE_BACKUP_DRIVE_AUTH_METHOD', default='service_account')
GOOGLE_BACKUP_OAUTH_CLIENT_SECRETS_FILE = get_config_value('GOOGLE_BACKUP_OAUTH_CLIENT_SECRETS_FILE', default='')
GOOGLE_BACKUP_OAUTH_TOKEN_FILE = get_config_value('GOOGLE_BACKUP_OAUTH_TOKEN_FILE', default='google_drive_backup_token.json')
GOOGLE_BACKUP_SERVICE_ACCOUNT_FILE = get_config_value('GOOGLE_BACKUP_SERVICE_ACCOUNT_FILE', default='')

# =============
# Custom User
# =============
AUTH_USER_MODEL = 'website.CustomUser'

# =============
# Onboarding
# =============
# Default temporary password assigned to newly onboarded users.
# Change this value in your .env or here before deployment.
DEFAULT_TEMP_PASSWORD = get_config_value('DEFAULT_TEMP_PASSWORD', default='student')

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
