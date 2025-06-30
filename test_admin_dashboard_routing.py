#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()
client = Client()

# Test admin login and dashboard redirect
try:
    admin = User.objects.get(username='admin')
    print(f"Testing login for admin user: {admin.username} (role: {admin.role})")
    
    # Login as admin
    login_success = client.login(username='admin', password='admin123')
    print(f"Login successful: {login_success}")
    
    if login_success:
        # Test dashboard access
        response = client.get('/dashboard/')
        print(f"Dashboard response status: {response.status_code}")
        
        if response.status_code == 200:
            print("Dashboard loaded successfully!")
            # Check if it's rendering the correct template
            template_names = [t.name for t in response.templates]
            print(f"Templates used: {template_names}")
        elif response.status_code == 302:
            print(f"Dashboard redirected to: {response.url}")
        else:
            print(f"Dashboard access failed with status: {response.status_code}")
    
except User.DoesNotExist:
    print("Admin user not found")
except Exception as e:
    print(f"Error during testing: {e}")
