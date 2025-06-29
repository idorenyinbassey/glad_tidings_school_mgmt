"""
Production settings for glad_school_portal project.

This file contains production-specific settings that prioritize security,
performance, and stability.
"""

from .settings import *
import environ

# Initialize environ for production
env = environ.Env(
    DEBUG=(bool, False),
    SECURE_SSL_REDIRECT=(bool, True),
    SESSION_COOKIE_SECURE=(bool, True),
    CSRF_COOKIE_SECURE=(bool, True),
    USE_HTTPS=(bool, True),
)

# Read production environment variables
environ.Env.read_env(os.path.join(BASE_DIR, '.env.production'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS Settings - enable only after testing SSL setup
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Additional security headers
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session security
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# CSRF security
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True

# File upload security
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Admin security
ADMIN_URL = env('ADMIN_URL', default='admin/')  # Allow custom admin URL

# Production logging configuration
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
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'production.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'glad_school_portal': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@gladtidingsschool.com')
SERVER_EMAIL = env('SERVER_EMAIL', default='admin@gladtidingsschool.com')

# Admin notifications
ADMINS = [
    ('Admin', env('ADMIN_EMAIL', default='admin@gladtidingsschool.com')),
]
MANAGERS = ADMINS

# Cache configuration for production
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'glad_school',
        'TIMEOUT': 300,  # 5 minutes default timeout
    }
}

# Session cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Template caching
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# Static files production settings
STATIC_ROOT = env('STATIC_ROOT', default=BASE_DIR / 'staticfiles')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Media files production settings
MEDIA_ROOT = env('MEDIA_ROOT', default=BASE_DIR / 'media')

# Database connection pooling and optimization
if env('DATABASE_URL', default=None):
    DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
    DATABASES['default']['OPTIONS'].update({
        'MAX_CONNS': 20,
        'pool_pre_ping': True,
    })

# Performance monitoring
INTERNAL_IPS = []  # Disable debug toolbar completely

# Content Security Policy for production
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src': ("'self'", "'unsafe-inline'", "https://code.jquery.com", "https://cdn.jsdelivr.net"),
        'style-src': ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"),
        'font-src': ("'self'", "https://fonts.gstatic.com"),
        'img-src': ("'self'", "data:", "https:"),
        'connect-src': ("'self'",),
        'frame-ancestors': ("'none'",),
        'base-uri': ("'self'",),
        'form-action': ("'self'",),
    }
}

# CORS settings for production (restrict as needed)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True

# REST Framework production settings
REST_FRAMEWORK.update({
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    },
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
})

# Remove debug toolbar from installed apps
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']

# Remove debug toolbar middleware
MIDDLEWARE = [m for m in MIDDLEWARE if 'debug_toolbar' not in m]

# Additional security middleware for production
MIDDLEWARE.insert(1, 'django.middleware.security.SecurityMiddleware')

# Health check endpoints
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # Disk usage percentage
    'MEMORY_MIN': 100,     # Minimum available memory in MB
}
