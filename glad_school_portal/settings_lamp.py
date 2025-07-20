"""
Django LAMP settings for Glad Tidings School Management Portal
This configuration is optimized for LAMP stack deployment
"""

from .settings import *
import pymysql

# Install PyMySQL as MySQLdb alternative (in case mysqlclient fails)
pymysql.install_as_MySQLdb()

# LAMP-specific database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env.str('DB_NAME', default='glad_school_db'),
        'USER': env.str('DB_USER', default='glad_user'),
        'PASSWORD': env.str('DB_PASSWORD', default=''),
        'HOST': env.str('DB_HOST', default='localhost'),
        'PORT': env.str('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'autocommit': True,
        },
        'CONN_MAX_AGE': 60,  # Keep connections alive for 60 seconds
    }
}

# Use database sessions instead of Redis (more LAMP-friendly)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_SECURE = True if not DEBUG else False
SESSION_COOKIE_HTTPONLY = True

# Database cache instead of Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
        'TIMEOUT': 300,  # 5 minutes default timeout
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,  # Delete 1/3 of cache when MAX_ENTRIES is reached
        }
    }
}

# Static files configuration for Apache serving
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/glad_school/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/glad_school/media/'

# WhiteNoise for static file serving (backup if Apache doesn't serve static files)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise early
] + [middleware for middleware in MIDDLEWARE[1:] if 'whitenoise' not in middleware]

# Static files optimization
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# WhiteNoise settings
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_MAX_AGE = 31536000 if not DEBUG else 0  # 1 year for production

# Apache-specific file upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Security settings for production LAMP
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_SECONDS = 31536000
    X_FRAME_OPTIONS = 'DENY'
    
    # Use secure cookies
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    
    # Force HTTPS
    SECURE_SSL_REDIRECT = True

# Logging configuration for LAMP environment
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/glad_school.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'apache_error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/apache2/glad_school_django_error.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'] if DEBUG else ['file', 'apache_error'],
            'level': 'INFO',
            'propagate': True,
        },
        'glad_school': {
            'handlers': ['file', 'console'] if DEBUG else ['file', 'apache_error'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Email configuration (same as original but explicit for LAMP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='Glad Tidings School <noreply@gladtidingsschool.example>')

# Performance optimizations for LAMP
if not DEBUG:
    # Template caching
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# MySQL-specific settings
DATABASES['default']['TEST'] = {
    'CHARSET': 'utf8mb4',
    'COLLATION': 'utf8mb4_unicode_ci',
}

# Time zone setting (important for MySQL)
USE_TZ = True
TIME_ZONE = 'UTC'

# Content Security Policy for Apache
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:", "https:")

# CORS settings (if needed for API access)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True

# Django REST Framework settings remain the same
REST_FRAMEWORK.update({
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
})

# Disable Redis-specific middleware and apps
INSTALLED_APPS = [app for app in INSTALLED_APPS if 'django_redis' not in app]
MIDDLEWARE = [middleware for middleware in MIDDLEWARE if 'redis' not in middleware.lower()]

# Add database cache creation command
INSTALLED_APPS += ['django.contrib.sessions']

print("LAMP settings loaded successfully!")
