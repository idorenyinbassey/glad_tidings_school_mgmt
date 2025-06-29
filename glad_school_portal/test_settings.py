# Test-specific settings that override the main settings
from .settings import *

# Disable debug toolbar in tests
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
}

# Remove debug toolbar from installed apps and middleware
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']
MIDDLEWARE = [middleware for middleware in MIDDLEWARE if 'debug_toolbar' not in middleware]

# Disable caching in tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Use in-memory database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Enable migrations in tests for system health checks
# Comment out the DisableMigrations class for full testing
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
    
#     def __getitem__(self, item):
#         return None

# MIGRATION_MODULES = DisableMigrations()

# Disable logging during tests
LOGGING_CONFIG = None
import logging
logging.disable(logging.CRITICAL)

# Disable CORS and CSP restrictions in tests
CORS_ALLOW_ALL_ORIGINS = True
CONTENT_SECURITY_POLICY = None

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable email sending in tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
