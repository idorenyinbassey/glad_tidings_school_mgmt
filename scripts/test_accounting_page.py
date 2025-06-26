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

def test_accounting_pages():
    print("Testing accounting pages...")
    
    # Get the User model
    User = get_user_model()
    
    # Find or create an admin user for testing
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            role='admin'
        )
    
    # Create a test client and log in as admin
    client = Client()
    logged_in = client.login(username='admin', password='adminpassword')
    
    print(f"User logged in: {logged_in}")
    
    # Test accounting home page
    print("\nTesting accounting home page...")
    home_url = '/accounting/'
    home_response = client.get(home_url)
    print(f"Status code: {home_response.status_code}")
    if home_response.status_code != 200:
        print(f"Error content: {home_response.content[:1000]}")
        
    # Test fees page
    print("\nTesting fees page...")
    fees_url = '/accounting/fees/'
    fees_response = client.get(fees_url)
    print(f"Status code: {fees_response.status_code}")
    if fees_response.status_code != 200:
        print(f"Error content: {fees_response.content[:1000]}")
    
    # Test reports page
    print("\nTesting reports page...")
    reports_url = '/accounting/reports/'
    reports_response = client.get(reports_url)
    print(f"Status code: {reports_response.status_code}")
    if reports_response.status_code != 200:
        print(f"Error content: {reports_response.content[:1000]}")

if __name__ == "__main__":
    test_accounting_pages()
