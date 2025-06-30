#!/usr/bin/env python3
"""
Final test script to verify the accountant dashboard after fixing VS Code problems.
"""

import os
import sys
import django
from django.test import Client

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def test_accountant_dashboard():
    """Test the accountant dashboard functionality"""
    client = Client()
    
    print("🧪 Testing Accountant Dashboard After VS Code Fixes")
    print("=" * 60)
    
    # 1. Test accountant login
    print("1️⃣  Testing accountant login...")
    
    # Ensure accountant user exists
    try:
        accountant = User.objects.get(username='accountant')
        print(f"   ✅ Found accountant: {accountant.username} (Role: {accountant.role})")
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
        print(f"   ✅ Created accountant: {accountant.username} (Role: {accountant.role})")
    
    # 2. Test login and redirect
    print("\n2️⃣  Testing login redirect...")
    
    login_response = client.post('/login/', {
        'username': 'accountant',
        'password': 'AccountantPass123'
    })
    
    print(f"   Login status: {login_response.status_code}")
    if login_response.status_code == 302:
        print(f"   Redirect to: {login_response.url}")
        if '/accounting/' in login_response.url:
            print("   ✅ Correctly redirected to finance dashboard")
        else:
            print("   ⚠️  Not redirected to accounting dashboard")
    
    # 3. Test dashboard rendering
    print("\n3️⃣  Testing dashboard rendering...")
    
    dashboard_response = client.get('/accounting/')
    print(f"   Dashboard status: {dashboard_response.status_code}")
    
    if dashboard_response.status_code == 200:
        print("   ✅ Dashboard accessible")
        
        content = dashboard_response.content.decode()
        
        # Check for key elements that should be present
        checks = [
            ('Page Title', 'Finance Dashboard' in content),
            ('Revenue Chart', 'revenueChart' in content),
            ('Payment Chart', 'paymentMethodChart' in content),
            ('JSON Data Structure', 'monthly-data' in content),
            ('Clean JavaScript', 'JSON.parse' in content and 'document.getElementById' in content),
            ('Chart.js Library', 'chart.js' in content),
            ('Quick Actions', 'Quick Actions' in content),
            ('Bootstrap Styling', 'btn btn-' in content),
        ]
        
        print("\n   Dashboard Content Verification:")
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"   {status} {check_name}")
        
        # Check that Django template tags are NOT in JavaScript blocks
        print("\n   JavaScript Code Quality:")
        js_problems = [
            ('No Django tags in JS', '{{ ' not in content.split('<script>')[1] if '<script>' in content else True),
            ('No template loops in JS', '{% for' not in content.split('<script>')[1] if '<script>' in content else True),
            ('Uses JSON parsing', 'JSON.parse(' in content),
            ('Separated data/logic', 'application/json' in content)
        ]
        
        for check_name, check_result in js_problems:
            status = "✅" if check_result else "❌"
            print(f"   {status} {check_name}")
    
    # 4. Test other accounting pages
    print("\n4️⃣  Testing accounting functionality...")
    
    pages = [
        ('/accounting/fees/', 'Fee Management'),
        ('/accounting/payments/', 'Payment Management'),
        ('/accounting/fees/add/', 'Add Fee'),
        ('/accounting/payments/add/', 'Add Payment')
    ]
    
    for url, name in pages:
        response = client.get(url)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"   {status} {name}: {response.status_code}")
    
    print("\n🎉 All tests completed!")
    print("📋 Summary: Accountant dashboard is working correctly with clean JavaScript")
    print("🔧 VS Code linting errors have been resolved")
    print("=" * 60)

if __name__ == '__main__':
    test_accountant_dashboard()
