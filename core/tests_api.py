from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser
from django.contrib.auth import get_user_model

class APITestCase(TestCase):
    """Test case to verify API endpoints and AJAX functionality"""
    
    def setUp(self):
        """Set up test data"""
        User = get_user_model()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin_api_test',
            email='admin_api@example.com',
            password='securepass123'
        )
        self.admin_user.role = 'admin'
        self.admin_user.is_staff = True
        self.admin_user.save()
        
        # Create student user
        self.student_user = User.objects.create_user(
            username='student_api_test',
            email='student_api@example.com',
            password='securepass123'
        )
        self.student_user.role = 'student'
        self.student_user.save()
        
        # Authenticated clients
        self.admin_client = Client()
        self.admin_client.login(username='admin_api_test', password='securepass123')
        
        self.student_client = Client()
        self.student_client.login(username='student_api_test', password='securepass123')
        
        # Anonymous client
        self.anonymous_client = Client()
    
    def test_public_api_access(self):
        """Test access to public pages that may have AJAX content"""
        # Testing access to landing page
        response = self.anonymous_client.get(reverse('landing_page'))
        self.assertEqual(response.status_code, 200)
        
        # Testing authenticated access to dashboard
        response = self.admin_client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_authenticated_endpoints(self):
        """Test that authenticated endpoints require login"""
        # Testing dashboard access requires authentication
        response = self.anonymous_client.get(reverse('dashboard'))
        self.assertIn(response.status_code, [302, 403])  # Either redirect to login or forbidden
        
        # Testing authenticated access works
        response = self.student_client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_role_based_access(self):
        """Test that different roles have appropriate access to pages"""
        # Test admin access to dashboard
        admin_response = self.admin_client.get(reverse('dashboard'))
        self.assertEqual(admin_response.status_code, 200)
        
        # Test student access to dashboard
        student_response = self.student_client.get(reverse('dashboard'))
        self.assertEqual(student_response.status_code, 200)
        
        # Verify admin and student see different dashboards
        # Skip content comparison tests by default since they might be too specific
        self.assertNotEqual(admin_response.content, student_response.content)
