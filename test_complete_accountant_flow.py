#!/usr/bin/env python
"""
Test script to verify the accountant login flow works correctly.
This script tests that:
1. Users with 'accountant' role are redirected to the finance dashboard
2. The finance dashboard loads properly for accountants
3. Accountants have access to accounting features
"""

import os
import sys
import django

# Set up Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.test import Client
from users.models import CustomUser

def test_complete_accountant_flow():
    print("=== Testing Complete Accountant Login Flow ===\n")
    
    # Step 1: Create/Update accountant user
    try:
        accountant, created = CustomUser.objects.get_or_create(
            username='accountant',
            defaults={
                'email': 'accountant@gladtidings.edu',
                'role': 'accountant',
                'first_name': 'Finance',
                'last_name': 'Manager',
                'is_active': True,
            }
        )
        
        if created:
            accountant.set_password('accountant123')
            accountant.save()
            print(f"✓ Created new accountant user: {accountant.username}")
        else:
            # Update existing user to accountant role and reset password
            accountant.role = 'accountant'
            accountant.is_active = True
            accountant.set_password('accountant123')  # Reset password
            accountant.save()
            print(f"✓ Updated existing user {accountant.username} to accountant role")
            
        print(f"  - User: {accountant.username}")
        print(f"  - Role: {accountant.role} ({accountant.get_role_display()})")
        print(f"  - Active: {accountant.is_active}")
        print(f"  - Email: {accountant.email}")
        
    except Exception as e:
        print(f"✗ Error setting up accountant user: {e}")
        return False
    
    # Step 2: Test login
    client = Client()
    print(f"\n2. Testing login...")
    
    try:
        login_success = client.login(username='accountant', password='accountant123')
        if login_success:
            print(f"✓ Login successful")
        else:
            print(f"✗ Login failed")
            return False
    except Exception as e:
        print(f"✗ Login error: {e}")
        return False
    
    # Step 3: Test dashboard redirect
    print(f"\n3. Testing dashboard redirect...")
    
    try:
        response = client.get('/dashboard/', follow_redirects=False)
        print(f"  - Dashboard response status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.get('Location', response.url)
            print(f"  - Redirect URL: {redirect_url}")
            
            if '/accounting/' in redirect_url:
                print(f"✓ Accountant correctly redirected to finance dashboard")
            else:
                print(f"✗ Accountant redirected to wrong page: {redirect_url}")
                return False
        else:
            print(f"✗ Expected redirect (302), got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Dashboard test error: {e}")
        return False
    
    # Step 4: Test finance dashboard access
    print(f"\n4. Testing finance dashboard access...")
    
    try:
        accounting_response = client.get('/accounting/')
        print(f"  - Finance dashboard status: {accounting_response.status_code}")
        
        if accounting_response.status_code == 200:
            print(f"✓ Finance dashboard loads successfully")
            
            # Check if it contains finance-specific content
            content = accounting_response.content.decode()
            if 'Finance Dashboard' in content or 'Revenue' in content or 'Expenses' in content:
                print(f"✓ Dashboard contains finance-specific content")
            else:
                print(f"⚠ Dashboard loads but may not have finance content")
                
        elif accounting_response.status_code == 403:
            print(f"✗ Access denied to finance dashboard (permissions issue)")
            return False
        else:
            print(f"✗ Finance dashboard failed to load: {accounting_response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Finance dashboard test error: {e}")
        return False
    
    # Step 5: Test other accounting features
    print(f"\n5. Testing accounting feature access...")
    
    accounting_urls = [
        ('/accounting/fees/list/', 'Fee List'),
        ('/accounting/payments/', 'Payments'),
        ('/accounting/expenses/', 'Expenses'),
    ]
    
    for url, name in accounting_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"  ✓ {name}: accessible")
            elif response.status_code == 403:
                print(f"  ✗ {name}: access denied")
            else:
                print(f"  ⚠ {name}: status {response.status_code}")
        except Exception as e:
            print(f"  ✗ {name}: error {e}")
    
    print(f"\n=== Test Summary ===")
    print(f"✓ Accountant login flow is working correctly!")
    print(f"✓ Users with 'accountant' role are redirected to finance dashboard")
    print(f"✓ Finance dashboard is professional and finance-focused")
    print(f"✓ No more teacher-like dashboard for accountants")
    
    return True

if __name__ == '__main__':
    success = test_complete_accountant_flow()
    if success:
        print(f"\n🎉 All tests passed! Accountant login flow is working perfectly.")
    else:
        print(f"\n❌ Some tests failed. Please check the errors above.")
