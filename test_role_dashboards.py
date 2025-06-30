#!/usr/bin/env python
"""
Test script to verify role-based dashboards and check for errors
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

def test_role_dashboards():
    print("🧪 Testing Role-Based Dashboard System")
    print("=" * 55)
    
    User = get_user_model()
    client = Client()
    
    # Test cases: (username, expected_redirect_or_template)
    test_cases = [
        ('admin', 'dashboard_admin.html'),
        ('accountant', '/accounting/'),
        ('student1', 'dashboard_student.html'),
    ]
    
    print("🔍 Testing each role's dashboard behavior:")
    
    for username, expected in test_cases:
        print(f"\n👤 Testing {username}:")
        
        try:
            user = User.objects.get(username=username)
            print(f"   Role: {user.role}")
            
            # Force login
            client.force_login(user)
            
            # Test dashboard access
            response = client.get('/dashboard/')
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 302:
                redirect_url = response.url
                print(f"   Redirects to: {redirect_url}")
                
                if expected.startswith('/'):
                    if expected in redirect_url:
                        print(f"   ✅ Correct redirect for {user.role}")
                    else:
                        print(f"   ❌ Wrong redirect for {user.role}! Expected {expected}")
                else:
                    print(f"   ❌ Should render template, not redirect for {user.role}")
                    
            elif response.status_code == 200:
                # Check if correct template was used
                template_names = [t.name for t in response.templates if t.name]
                print(f"   Templates used: {template_names}")
                
                if expected in template_names:
                    print(f"   ✅ Correct template for {user.role}")
                else:
                    print(f"   ❌ Wrong template for {user.role}! Expected {expected}")
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                
        except User.DoesNotExist:
            print(f"   ❌ User {username} does not exist")
        except Exception as e:
            print(f"   ❌ Error testing {username}: {e}")
    
    print(f"\n🎯 Testing accountant dashboard for errors:")
    
    # Test accountant dashboard specifically
    try:
        accountant = User.objects.get(username='accountant')
        client.force_login(accountant)
        
        response = client.get('/accounting/')
        print(f"   Accounting dashboard status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Accounting dashboard loads successfully")
            
            # Check for any context errors
            if hasattr(response, 'context'):
                context = response.context
                error_keys = [key for key in context.keys() if 'error' in key.lower()]
                if error_keys:
                    print(f"   ⚠️  Error context keys found: {error_keys}")
                else:
                    print(f"   ✅ No error context keys found")
            
        else:
            print(f"   ❌ Accounting dashboard failed to load")
            
    except Exception as e:
        print(f"   ❌ Error testing accountant dashboard: {e}")

if __name__ == '__main__':
    test_role_dashboards()
