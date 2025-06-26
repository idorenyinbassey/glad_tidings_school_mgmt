from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UrlAccessTests(TestCase):
    """Test case to verify URL accessibility based on user roles"""
    
    def setUp(self):
        """Set up test data - create users with different roles"""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="admin_user",
            email="admin@example.com",
            password="adminpass123",
            role="admin"
        )
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        # Create staff user
        self.staff_user = User.objects.create_user(
            username="staff_user",
            email="staff@example.com",
            password="staffpass123",
            role="staff"
        )
        
        # Create student user
        self.student_user = User.objects.create_user(
            username="student_user",
            email="student@example.com",
            password="studentpass123",
            role="student"
        )
        
        # Create client
        self.client = Client()
    
    def test_login_page_accessible(self):
        """Test that login page is accessible to unauthenticated users"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
    
    def test_admin_can_access_dashboard(self):
        """Test that admin user can access admin dashboard"""
        # Login as admin
        self.client.login(username="admin_user", password="adminpass123")
        
        # Check dashboard access
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
