#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.test import Client
from users.models import CustomUser

def test_accountant_login():
    print("=== Testing Accountant Login Flow ===")
    
    # Create or get accountant user
    try:
        accountant, created = CustomUser.objects.get_or_create(
            username='accountant',
            defaults={
                'email': 'accountant@gladtidings.edu',
                'role': 'accountant',
                'first_name': 'Finance',
                'last_name': 'Manager'
            }
        )
        if created:
            accountant.set_password('accountant123')
            accountant.save()
            print(f"✓ Created accountant user: {accountant.username}")
        else:
            accountant.role = 'accountant'
            accountant.save()
            print(f"✓ Updated user {accountant.username} to accountant role")
            
        print(f"User role: {accountant.role} ({accountant.get_role_display()})")
        
    except Exception as e:
        print(f"✗ Error creating accountant user: {e}")
        return
    
    # Test login flow
    client = Client()
    
    # Test login
    login_success = client.login(username='accountant', password='accountant123')
    if login_success:
        print("✓ Accountant login successful")
    else:
        print("✗ Accountant login failed")
        return
    
    # Test dashboard redirect
    try:
        response = client.get('/dashboard/')
        print(f"Dashboard response status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_location = response.get('Location', '')
            print(f"✓ Dashboard redirects to: {redirect_location}")
            
            # Test if it redirects to accounting
            if '/accounting/' in redirect_location:
                print("✓ Accountant correctly redirected to finance dashboard")
                
                # Test the accounting dashboard loads
                accounting_response = client.get('/accounting/')
                if accounting_response.status_code == 200:
                    print("✓ Finance dashboard loads successfully")
                else:
                    print(f"✗ Finance dashboard failed to load: {accounting_response.status_code}")
            else:
                print("✗ Accountant not redirected to finance dashboard")
        else:
            print(f"✗ Dashboard should redirect, got status {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error testing dashboard: {e}")
    
    print("=== Test Complete ===")

if __name__ == '__main__':
    test_accountant_login()
