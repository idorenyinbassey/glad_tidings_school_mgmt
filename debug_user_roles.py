#!/usr/bin/env python
"""
Debug script to check current user roles and dashboard redirection issue
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

def debug_user_roles():
    print("🔍 DEBUG: User Roles and Dashboard Issue")
    print("=" * 50)
    
    User = get_user_model()
    
    print("1️⃣ Checking all users in database:")
    users = User.objects.all()
    for user in users:
        print(f"   👤 {user.username}: role='{user.role}', superuser={user.is_superuser}, staff={user.is_staff}")
    
    print(f"\n2️⃣ Total users found: {users.count()}")
    
    # Test dashboard logic
    print(f"\n3️⃣ Testing dashboard logic for each user:")
    client = Client()
    
    for user in users:
        print(f"\n   Testing user: {user.username} (role: {user.role})")
        
        # Force login
        client.force_login(user)
        
        # Test dashboard
        response = client.get('/dashboard/')
        print(f"   Dashboard response: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.url
            print(f"   Redirects to: {redirect_url}")
            
            # Check what this tells us about role logic
            if user.role == 'admin' and '/accounting/' in redirect_url:
                print(f"   ❌ PROBLEM: Admin user redirected to accounting dashboard!")
            elif user.role == 'accountant' and '/accounting/' not in redirect_url:
                print(f"   ❌ PROBLEM: Accountant not redirected to accounting dashboard!")
            else:
                print(f"   ✅ Correct redirect for role '{user.role}'")
        else:
            print(f"   Dashboard renders directly (status: {response.status_code})")
    
    print(f"\n4️⃣ Checking if admin user has wrong role:")
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            print(f"   Superuser found: {admin_user.username} with role '{admin_user.role}'")
            if admin_user.role != 'admin':
                print(f"   ❌ ISSUE: Superuser has role '{admin_user.role}' instead of 'admin'")
                return admin_user
            else:
                print(f"   ✅ Superuser has correct role")
        else:
            print(f"   ❌ No superuser found!")
    except Exception as e:
        print(f"   ❌ Error checking superuser: {e}")
    
    return None

if __name__ == '__main__':
    problematic_user = debug_user_roles()
    
    if problematic_user:
        print(f"\n🔧 FIXING: Setting {problematic_user.username} role to 'admin'")
        problematic_user.role = 'admin'
        problematic_user.save()
        print(f"✅ Fixed! {problematic_user.username} now has role 'admin'")
