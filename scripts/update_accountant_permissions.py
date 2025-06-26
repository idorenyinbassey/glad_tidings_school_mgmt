"""
Script to update the accountant user permissions
"""

import os
import django
import sys

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def update_accountant_permissions():
    """Update accountant user's permissions"""
    try:
        # Get the accountant user
        accountant = User.objects.get(username='accountant')
        print(f"Found accountant user: {accountant.username}")
        print(f"Current settings - Role: {accountant.role}, Is staff: {accountant.is_staff}, Is superuser: {accountant.is_superuser}")
        
        # Update permissions
        accountant.is_staff = True
        accountant.save()
        
        print(f"Updated settings - Role: {accountant.role}, Is staff: {accountant.is_staff}, Is superuser: {accountant.is_superuser}")
        print("Accountant permissions updated successfully!")
        
    except User.DoesNotExist:
        print("Accountant user not found")
    except Exception as e:
        print(f"Error updating accountant permissions: {e}")

if __name__ == "__main__":
    update_accountant_permissions()
