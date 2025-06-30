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

# Clear any existing sessions
Session.objects.all().delete()
print("Cleared all sessions")

# Create a fresh client
client = Client()

try:
    admin = User.objects.get(username='admin')
    print(f"Testing with admin user: {admin.username} (role: {admin.role})")
    
    # Test step by step
    print("\n1. Testing login...")
    login_data = {'username': 'admin', 'password': 'admin123'}
    login_response = client.post('/accounts/login/', login_data, follow=True)
    print(f"Login response status: {login_response.status_code}")
    print(f"Login redirect chain: {[r[0] for r in login_response.redirect_chain]}")
    
    print("\n2. Testing direct dashboard access...")
    dashboard_response = client.get('/dashboard/', follow=True)
    print(f"Dashboard response status: {dashboard_response.status_code}")
    print(f"Dashboard redirect chain: {[r[0] for r in dashboard_response.redirect_chain]}")
    
    if dashboard_response.status_code == 200:
        template_names = [t.name for t in dashboard_response.templates if hasattr(t, 'name')]
        print(f"Templates used: {template_names}")
        
        # Check if admin dashboard template is being used
        if 'core/dashboard_admin.html' in template_names:
            print("✓ CORRECT: Admin dashboard template is being used!")
        elif 'accounting/accounting_home.html' in template_names:
            print("✗ WRONG: Accounting dashboard template is being used!")
        else:
            print(f"? UNEXPECTED: Other template being used: {template_names}")
    
except User.DoesNotExist:
    print("Admin user not found")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
