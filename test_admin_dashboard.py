#!/usr/bin/env python
"""
Simple test to verify admin dashboard access
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

def test_admin_dashboard():
    print("🔍 Testing Admin Dashboard Access")
    print("=" * 40)
    
    User = get_user_model()
    client = Client()
    
    try:
        # Get admin user
        admin_user = User.objects.get(username='admin')
        print(f"Admin user: {admin_user.username}, Role: {admin_user.role}")
        
        # Login as admin
        login_success = client.login(username='admin', password='admin123')
        print(f"Login successful: {login_success}")
        
        if not login_success:
            print("❌ Login failed - cannot test dashboard")
            return
        
        # Test dashboard access
        print("\n📊 Testing dashboard access...")
        response = client.get('/dashboard/')
        print(f"Dashboard response status: {response.status_code}")
        
        if response.status_code == 302:
            print(f"❌ Admin redirected instead of rendering admin dashboard")
            print(f"Redirect URL: {response.url}")
        elif response.status_code == 200:
            print(f"✅ Admin dashboard rendered successfully")
            template_names = [t.name for t in response.templates if 'dashboard_admin' in t.name]
            if template_names:
                print(f"✅ Correct admin template used: {template_names}")
            else:
                all_templates = [t.name for t in response.templates if t.name and 'dashboard' in t.name]
                print(f"⚠️  Templates used: {all_templates}")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
        # Test accountant dashboard for comparison
        print(f"\n📊 Testing accountant dashboard for comparison...")
        accountant_user = User.objects.get(username='accountant')
        client.force_login(accountant_user)
        
        response = client.get('/dashboard/')
        print(f"Accountant dashboard status: {response.status_code}")
        if response.status_code == 302:
            print(f"✅ Accountant correctly redirected to: {response.url}")
        
        # Test accounting dashboard directly
        response = client.get('/accounting/')
        print(f"Accounting dashboard status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Accounting dashboard loads successfully")
        else:
            print(f"❌ Accounting dashboard failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_admin_dashboard()
