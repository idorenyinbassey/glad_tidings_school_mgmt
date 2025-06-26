from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class APITests(TestCase):
    """Test case to verify API endpoints and AJAX functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username="api_test_user",
            email="apitest@example.com",
            password="apipass123",
            role="admin"
        )
        
        # Create client and login
        self.client = Client()
        self.client.login(username="api_test_user", password="apipass123")
    
    def test_api_authentication(self):
        """Test API authentication"""
        # Logout to test unauthenticated access
        self.client.logout()
        
        # Try to access an API endpoint that requires authentication
        response = self.client.get(reverse('api-endpoint'))  # Replace with your actual API endpoint
        # Should redirect to login or return 403/401
        self.assertIn(response.status_code, [302, 401, 403])
        
        # Login and try again
        self.client.login(username="api_test_user", password="apipass123")
        response = self.client.get(reverse('api-endpoint'))  # Replace with your actual API endpoint
        # Should be successful now
        self.assertEqual(response.status_code, 200)
