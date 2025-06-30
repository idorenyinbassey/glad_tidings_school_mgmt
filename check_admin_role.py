#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Get admin user
try:
    admin = User.objects.get(username='admin')
    print(f"Admin user found:")
    print(f"Username: {admin.username}")
    print(f"Role: {admin.role}")
    print(f"Is superuser: {admin.is_superuser}")
    print(f"Is staff: {admin.is_staff}")
except User.DoesNotExist:
    print("No admin user found")

# List all users and their roles
print("\nAll users and their roles:")
for user in User.objects.all():
    print(f"- {user.username}: {user.role} (superuser: {user.is_superuser})")
