# settings_ci.py - CI/CD Testing Settings
"""
Django settings for CI/CD testing with both PostgreSQL and MySQL support.
This settings file automatically detects the database type from DATABASE_URL.
"""

import os
from urllib.parse import urlparse

# Try to import base settings with fallback
try:
    from .settings import *
except ImportError:
    # Fallback if base settings cannot be imported
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        # Add your apps here
        'core',
        'users',
        'students',
        'staff',
        'accounting',
        'academics',
    ]
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
    ROOT_URLCONF = 'glad_school_portal.urls'
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
    WSGI_APPLICATION = 'glad_school_portal.wsgi.application'
    USE_TZ = True
    STATIC_URL = '/static/'

# Override settings for CI/CD testing
DEBUG = False
TESTING = True

# Security - Use test keys only
SECRET_KEY = os.environ.get('SECRET_KEY', 'test-secret-key-for-ci-cd-only-very-long-and-secure')

# Database configuration based on DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgres://postgres:postgres@localhost:5432/test_db')
url = urlparse(DATABASE_URL)

if url.scheme == 'mysql':
    # MySQL configuration for CI
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': url.path[1:],  # Remove leading slash
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port or 3306,
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
            'TEST': {
                'NAME': f'test_{url.path[1:]}',
                'CHARSET': 'utf8mb4',
                'COLLATION': 'utf8mb4_unicode_ci',
            }
        }
    }
else:
    # PostgreSQL configuration for CI (default)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': url.path[1:],  # Remove leading slash
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port or 5432,
            'TEST': {
                'NAME': f'test_{url.path[1:]}',
            }
        }
    }

# Cache - Use dummy cache for CI
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Session storage - Use database sessions for CI
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Media and static files for CI
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')
STATIC_ROOT = os.path.join(BASE_DIR, 'test_static')

# Logging configuration for CI
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'glad_school_portal': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

# Disable migrations for faster testing (optional)
# Uncomment if migrations are slowing down CI
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# 
# if 'DISABLE_MIGRATIONS' in os.environ:
#     MIGRATION_MODULES = DisableMigrations()

# Test-specific security settings
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Disable password validators for faster tests
AUTH_PASSWORD_VALIDATORS = []

# Speed up password hashing in tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

print(f"CI Settings loaded with {url.scheme.upper()} database: {DATABASES['default']['NAME']}")
