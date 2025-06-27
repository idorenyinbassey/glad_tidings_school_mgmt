"""
Development settings for glad_school_portal project.
"""

from glad_school_portal.settings import *

# Override security settings for development
DEBUG = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# Simplified CSP for development
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'", "'unsafe-inline'", "'unsafe-eval'", "data:", "http:", "https:"),
    }
}

# Make sure Django doesn't redirect HTTP to HTTPS
MIDDLEWARE = [m for m in MIDDLEWARE if not m.endswith('RedirectMiddleware')]

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
