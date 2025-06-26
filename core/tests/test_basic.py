from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class BasicTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            role="admin"
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_admin_login(self):
        # Test that admin user can log in
        login_successful = self.client.login(
            username="testuser",
            password="testpassword123"
        )
        self.assertTrue(login_successful)

    def test_dashboard_redirect_when_logged_in(self):
        # Log in the user
        self.client.login(username="testuser", password="testpassword123")
        
        # Access the login page when already logged in
        response = self.client.get(reverse('login'), follow=True)
        
        # Should redirect to dashboard
        self.assertRedirects(response, reverse('dashboard'))

    def test_dashboard_requires_login(self):
        # Try accessing dashboard without logging in
        response = self.client.get(reverse('dashboard'))
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, 
            f"{reverse('login')}?next={reverse('dashboard')}"
        )
