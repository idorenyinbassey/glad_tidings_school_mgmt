#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Debug what happens when we check the admin role in the dashboard logic
try:
    admin = User.objects.get(username='admin')
    print(f"Admin user: {admin.username}")
    print(f"Admin role: {repr(admin.role)}")
    print(f"Admin role type: {type(admin.role)}")
    print(f"Role == 'admin': {admin.role == 'admin'}")
    print(f"Role == 'accountant': {admin.role == 'accountant'}")
    
    # Test the exact logic from the dashboard view
    role = getattr(admin, 'role', None)
    print(f"getattr result: {repr(role)}")
    
    if role == 'student':
        print("Would redirect to student dashboard")
    elif role == 'staff':
        print("Would redirect to staff dashboard")
    elif role == 'admin':
        print("Would render admin dashboard - THIS IS CORRECT!")
    elif role == 'accountant':
        print("Would redirect to accounting dashboard - THIS IS WRONG FOR ADMIN!")
    elif role == 'it_support':
        print("Would redirect to IT dashboard")
    else:
        print("Would render default dashboard")
        
except User.DoesNotExist:
    print("Admin user not found")
