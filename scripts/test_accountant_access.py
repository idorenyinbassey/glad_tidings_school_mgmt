"""
Test script to check if accountant can access the accounting page
"""

import os
import django
import sys

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
os.environ['ALLOWED_HOSTS'] = 'testserver'
django.setup()

from django.test.client import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def test_accountant_access():
    """Test if accountant can access the accounting page"""
    print("\nTesting accountant access to accounting page...")
    
    # Get accountant user
    try:
        accountant = User.objects.get(username='accountant')
        print(f"Found accountant user: {accountant.username}, role: {accountant.role}")
    except User.DoesNotExist:
        print("Accountant user not found!")
        return
    
    # Create a test client
    client = Client()
    logged_in = client.login(username='accountant', password='AccountPass123!')
    print(f"Login successful: {logged_in}")
    
    if not logged_in:
        print("Failed to log in as accountant!")
        return
    
    # Test access to accounting home page
    try:
        response = client.get('/accounting/')
        print(f"Accounting page status code: {response.status_code}")
        if response.status_code == 200:
            print("Accountant can access accounting page!")
        else:
            print(f"Accountant cannot access accounting page. Status code: {response.status_code}")
            
        # Print the context data
        if hasattr(response, 'context'):
            print("\nContext data:")
            for key, value in response.context.items():
                print(f"{key}: {value}")
        
    except Exception as e:
        print(f"Error accessing accounting page: {e}")
    
    # Test access to dashboard
    try:
        response = client.get('/dashboard/')
        print(f"\nDashboard page status code: {response.status_code}")
        if response.status_code == 200:
            print("Accountant can access dashboard page!")
            # Check which template was used
            if hasattr(response, 'templates') and response.templates:
                template_names = [t.name for t in response.templates]
                print(f"Dashboard templates used: {template_names}")
        else:
            print(f"Accountant cannot access dashboard. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error accessing dashboard page: {e}")

# Run the test
if __name__ == "__main__":
    test_accountant_access()
