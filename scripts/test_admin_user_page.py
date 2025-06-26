#!/usr/bin/env python
import os
import sys
import django

# Add project directory to path so Django can find settings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib import admin

def test_admin_user_page():
    print("Testing admin user change page...")
    
    # Get the User model
    User = get_user_model()
    
    # Find or create a superuser for testing
    try:
        admin_user = User.objects.get(username='admin')
        # Reset password to ensure it's correct
        admin_user.set_password('adminpassword123')
        admin_user.save()
        print("Using existing admin user")
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword123',
            role='admin'
        )
        print("Created new admin user")
    
    # Create a test client and log in as admin
    client = Client()
    logged_in = client.login(username='admin', password='adminpassword123')
    
    print(f"User logged in: {logged_in}")
    
    if not logged_in:
        print("Login failed, cannot test admin page without authentication")
        return
    
    # Get the first user's ID to test the page
    first_user = User.objects.all().first()
    if first_user:
        user_id = first_user.id
        
        # Test accessing the user change page
        change_url = f'/admin/users/customuser/{user_id}/change/'
        print(f"Testing URL: {change_url}")
        
        response = client.get(change_url)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Success! Admin user change page is working correctly.")
        else:
            print(f"Error: {response.content[:500]}")
    else:
        print("No users found in the database!")

if __name__ == "__main__":
    test_admin_user_page()
