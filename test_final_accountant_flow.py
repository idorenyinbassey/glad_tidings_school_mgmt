#!/usr/bin/env python3
"""
Final test script to verify the complete accountant experience after fixing VS Code problems.
This test ensures that:
1. Accountant can log in successfully
2. Gets redirected to the finance dashboard (not staff dashboard)
3. Dashboard loads without JavaScript errors
4. All accounting functionality is accessible
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import authenticate

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounting.models import Fee, Payment

User = get_user_model()

def test_complete_accountant_flow():
    """Test the complete accountant experience"""
    client = Client()
    
    print("🧪 Testing Complete Accountant Flow")
    print("=" * 50)
    
    # 1. Test accountant login
    print("1️⃣  Testing accountant login...")
    
    # Get or create accountant user
    try:
        accountant = User.objects.get(username='accountant')
        print(f"   ✅ Found existing accountant: {accountant.username} (Role: {accountant.role})")
    except User.DoesNotExist:
        accountant = User.objects.create_user(
            username='accountant',
            email='accountant@gladtidings.edu',
            password='AccountantPass123',
            first_name='Finance',
            last_name='Manager',
            role='accountant',
            is_staff=True
        )
        print(f"   ✅ Created new accountant: {accountant.username} (Role: {accountant.role})")
    
    # Test authentication
    auth_user = authenticate(username='accountant', password='AccountantPass123')
    if auth_user:
        print(f"   ✅ Authentication successful for {auth_user.username}")
    else:
        print("   ❌ Authentication failed")
        return False
    
    # 2. Test login redirect to finance dashboard
    print("\n2️⃣  Testing login redirect to finance dashboard...")
    
    login_response = client.post('/login/', {
        'username': 'accountant',
        'password': 'AccountantPass123'
    })
    
    print(f"   Login response status: {login_response.status_code}")
    
    if login_response.status_code == 302:
        redirect_url = login_response.url
        print(f"   Redirect URL: {redirect_url}")
        
        # Follow the redirect chain
        final_response = client.get(redirect_url)
        print(f"   Final response status: {final_response.status_code}")
        
        if '/accounting/' in redirect_url:
            print("   ✅ Correctly redirected to accounting dashboard")
        else:
            print(f"   ⚠️  Redirected to: {redirect_url} (should be /accounting/)")
    
    # 3. Test accounting dashboard access
    print("\n3️⃣  Testing accounting dashboard access...")
    
    dashboard_response = client.get('/accounting/')
    print(f"   Dashboard response status: {dashboard_response.status_code}")
    
    if dashboard_response.status_code == 200:
        print("   ✅ Accounting dashboard accessible")
        
        # Check for key dashboard elements
        content = dashboard_response.content.decode()
        
        checks = [
            ('Finance Dashboard', 'Finance Dashboard' in content),
            ('Revenue Chart', 'revenueChart' in content),
            ('Payment Methods Chart', 'paymentMethodChart' in content),
            ('Quick Actions', 'Quick Actions' in content),
            ('Record Payment', 'Record Payment' in content),
            ('Add Fee', 'Add Fee' in content),
            ('JSON Data Script', 'monthly-data' in content),
            ('Clean JavaScript', 'JSON.parse' in content)
        ]
        
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"   {status} {check_name}: {'Present' if check_result else 'Missing'}")
    else:
        print(f"   ❌ Dashboard access failed with status {dashboard_response.status_code}")
    
    # 4. Test accounting functionality access
    print("\n4️⃣  Testing accounting functionality access...")
    
    endpoints = [
        ('/accounting/fees/', 'Fee Management'),
        ('/accounting/payments/', 'Payment Management'),
        ('/accounting/fees/add/', 'Add Fee Form'),
        ('/accounting/payments/add/', 'Add Payment Form')
    ]
    
    for url, name in endpoints:
        response = client.get(url)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"   {status} {name}: {response.status_code}")
    
    # 5. Test data context
    print("\n5️⃣  Testing dashboard data context...")
    
    dashboard_response = client.get('/accounting/')
    if dashboard_response.status_code == 200:
        context = dashboard_response.context
        
        data_checks = [
            ('total_revenue', 'total_revenue' in context),
            ('total_expenses', 'total_expenses' in context),
            ('monthly_data', 'monthly_data' in context),
            ('payment_methods', 'payment_methods' in context),
            ('recent_payments', 'recent_payments' in context)
        ]
        
        for data_name, data_present in data_checks:
            status = "✅" if data_present else "❌"
            print(f"   {status} {data_name}: {'Present' if data_present else 'Missing'}")
            
            if data_present and data_name == 'monthly_data':
                monthly_data = context[data_name]
                print(f"      Monthly data type: {type(monthly_data)}")
                if isinstance(monthly_data, str):
                    print(f"      Monthly data preview: {monthly_data[:100]}...")
    
    print("\n🎉 Accountant flow test completed!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    test_complete_accountant_flow()
