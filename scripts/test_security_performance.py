#!/usr/bin/env python
"""
Test script to verify security and performance improvements.
"""

import os
import sys
import django
import time
import json
from urllib.parse import urljoin

# Add project directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.conf import settings
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse

User = get_user_model()

def test_security_settings():
    """
    Test that security settings are configured correctly.
    """
    print("\n=== SECURITY SETTINGS VERIFICATION ===")
    
    security_settings = {
        'DEBUG': settings.DEBUG,
        'SECRET_KEY': settings.SECRET_KEY[:5] + '*****',
        'SECURE_SSL_REDIRECT': getattr(settings, 'SECURE_SSL_REDIRECT', False),
        'SESSION_COOKIE_SECURE': getattr(settings, 'SESSION_COOKIE_SECURE', False),
        'CSRF_COOKIE_SECURE': getattr(settings, 'CSRF_COOKIE_SECURE', False),
        'SECURE_HSTS_SECONDS': getattr(settings, 'SECURE_HSTS_SECONDS', 0),
        'SECURE_BROWSER_XSS_FILTER': getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False),
        'SECURE_CONTENT_TYPE_NOSNIFF': getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False),
        'X_FRAME_OPTIONS': getattr(settings, 'X_FRAME_OPTIONS', None),
        'CSP Enabled': hasattr(settings, 'CSP_DEFAULT_SRC'),
    }
    
    print(json.dumps(security_settings, indent=4))
    
    # Verify password validators
    print("\nPassword validators:")
    for validator in settings.AUTH_PASSWORD_VALIDATORS:
        print(f"- {validator['NAME']}")
    
    # Verify middleware
    print("\nSecurity-related middleware:")
    security_middleware = [m for m in settings.MIDDLEWARE if 'security' in m.lower() or 'csrf' in m.lower() or 'csp' in m.lower()]
    for middleware in security_middleware:
        print(f"- {middleware}")

def test_db_performance():
    """
    Test database query performance.
    """
    print("\n=== DATABASE QUERY PERFORMANCE ===")
    
    # Clear cache to ensure fair testing
    cache.clear()
    
    # Test query with standard filter
    with CaptureQueriesContext(connection) as ctx:
        start_time = time.time()
        from accounting.models import TuitionFee
        fees = list(TuitionFee.objects.filter(status='unpaid').values('id', 'student__user__first_name', 'amount_due'))
        elapsed = time.time() - start_time
        print(f"Query for unpaid fees completed in {elapsed:.4f}s")
        print(f"Number of queries: {len(ctx.captured_queries)}")
        
        # Print the first 3 records
        print(f"Retrieved {len(fees)} records")
        for fee in fees[:3]:
            print(f"- {fee}")
    
    # Test query with select_related for related objects
    with CaptureQueriesContext(connection) as ctx:
        start_time = time.time()
        from students.models import StudentProfile
        students = list(StudentProfile.objects.select_related('user').all()[:10])
        elapsed = time.time() - start_time
        print(f"\nQuery for students with select_related completed in {elapsed:.4f}s")
        print(f"Number of queries: {len(ctx.captured_queries)}")
        print(f"Retrieved {len(students)} records")
    
    # Test prefetch_related for many-to-one relationships
    with CaptureQueriesContext(connection) as ctx:
        start_time = time.time()
        from accounting.models import TuitionFee
        tuition_fees = list(TuitionFee.objects.prefetch_related('payments').all()[:5])
        payment_count = sum(fee.payments.count() for fee in tuition_fees)
        elapsed = time.time() - start_time
        print(f"\nQuery for fees with payments (prefetch_related) completed in {elapsed:.4f}s")
        print(f"Number of queries: {len(ctx.captured_queries)}")
        print(f"Retrieved {len(tuition_fees)} fees with {payment_count} payments")

def test_cache_functionality():
    """
    Test caching functionality.
    """
    print("\n=== CACHE FUNCTIONALITY ===")
    
    # Check cache backend
    print(f"Cache backend: {settings.CACHES['default']['BACKEND']}")
    
    # Test basic caching
    cache.set('test_key', 'test_value', 30)
    retrieved = cache.get('test_key')
    print(f"Cache get/set working: {retrieved == 'test_value'}")
    
    # Test cache for a view
    client = Client()
    
    # First request should cache the response
    start_time = time.time()
    response1 = client.get('/')
    time1 = time.time() - start_time
    
    # Second request should be faster if caching is working
    start_time = time.time()
    response2 = client.get('/')
    time2 = time.time() - start_time
    
    print(f"First request: {time1:.4f}s")
    print(f"Second request: {time2:.4f}s")
    print(f"Improvement: {(time1-time2)/time1*100:.1f}%")
    
    # Clear the cache
    cache.clear()

def test_template_caching():
    """
    Test template rendering with caching.
    """
    print("\n=== TEMPLATE RENDERING ===")
    
    from django.template import Template, Context
    
    # Create a complex template
    template_code = """
    {% for i in range %}
        <div>{{ i }}</div>
        {% if i|divisibleby:2 %}
            <span>Even number</span>
        {% else %}
            <span>Odd number</span>
        {% endif %}
    {% endfor %}
    """
    
    # First render (cold cache)
    template = Template(template_code)
    context = Context({'range': range(100)})
    start_time = time.time()
    output = template.render(context)
    time1 = time.time() - start_time
    
    # Second render (should be cached if loader caching is working)
    template = Template(template_code)
    context = Context({'range': range(100)})
    start_time = time.time()
    output = template.render(context)
    time2 = time.time() - start_time
    
    print(f"First render: {time1:.4f}s")
    print(f"Second render: {time2:.4f}s")
    print(f"Improvement: {(time1-time2)/time1*100:.1f}%")

def run_all_tests():
    """
    Run all tests.
    """
    print("=== GLADTIDINGS SCHOOL PORTAL SECURITY & PERFORMANCE TEST ===\n")
    
    test_security_settings()
    test_db_performance()
    test_cache_functionality()
    test_template_caching()
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    run_all_tests()
