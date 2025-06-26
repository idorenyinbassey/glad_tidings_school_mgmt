#!/usr/bin/env python
import os
import sys
import django

# Add project directory to path so Django can find settings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.contrib.auth import get_user_model

def reset_admin_password():
    print("Resetting admin password...")
    
    # Get the User model
    User = get_user_model()
    
    # Find the admin user
    try:
        admin_user = User.objects.get(username='admin')
        # Set new password
        new_password = "Admin123!"
        admin_user.set_password(new_password)
        admin_user.save()
        print(f"Admin password has been reset to: {new_password}")
        print(f"Username: {admin_user.username}")
        print(f"Email: {admin_user.email}")
        print(f"Active: {admin_user.is_active}")
        print(f"Staff: {admin_user.is_staff}")
        print(f"Superuser: {admin_user.is_superuser}")
    except User.DoesNotExist:
        print("Admin user not found.")
        print("Creating new admin user...")
        User.objects.create_superuser(
            username='admin',
            email='admin@gladtidings.com',
            password='Admin123!',
            role='admin'
        )
        print("New admin user created with password: Admin123!")

if __name__ == "__main__":
    reset_admin_password()
