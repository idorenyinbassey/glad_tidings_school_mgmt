#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session

User = get_user_model()

def test_user_dashboard(username, password, expected_template):
    # Clear sessions and create fresh client
    Session.objects.all().delete()
    client = Client()
    
    try:
        user = User.objects.get(username=username)
        print(f"\n--- Testing {username} (role: {user.role}) ---")
        
        # Login
        login_data = {'username': username, 'password': password}
        login_response = client.post('/accounts/login/', login_data, follow=True)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            # Check dashboard
            dashboard_response = client.get('/dashboard/', follow=True)
            print(f"Dashboard status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                template_names = [t.name for t in dashboard_response.templates if hasattr(t, 'name')]
                main_templates = [t for t in template_names if not t.startswith('debug_toolbar') and not t.startswith('django/')]
                print(f"Main templates: {main_templates}")
                
                if expected_template in template_names:
                    print(f"✓ CORRECT: {username} sees the expected dashboard!")
                else:
                    print(f"✗ WRONG: {username} should see {expected_template} but sees {main_templates}")
            else:
                print(f"Dashboard access failed: {dashboard_response.status_code}")
        else:
            print(f"Login failed: {login_response.status_code}")
            
    except User.DoesNotExist:
        print(f"User {username} not found")
    except Exception as e:
        print(f"Error testing {username}: {e}")

# Test both roles
test_user_dashboard('admin', 'admin123', 'core/dashboard_admin.html')
test_user_dashboard('accountant', 'accountant123', 'accounting/accounting_home.html')
