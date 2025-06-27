from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import CustomUser

class SuperuserCreationTest(TestCase):
    def test_create_superuser_role(self):
        """Test that superusers are created with the 'admin' role by default"""
        User = get_user_model()
        
        # Create a test superuser
        admin_user = User.objects.create_superuser(
            username="testadmin",
            email="admin@example.com",
            password="adminpassword"
        )
        
        # Check that the role is set to 'admin'
        self.assertEqual(admin_user.role, "admin")
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
        
    def test_create_regular_user_role(self):
        """Test that regular users still get the default 'student' role"""
        User = get_user_model()
        
        # Create a regular user
        regular_user = User.objects.create_user(
            username="teststudent",
            email="student@example.com",
            password="studentpassword"
        )
        
        # Check that the role is set to the default 'student'
        self.assertEqual(regular_user.role, "student")
        self.assertFalse(regular_user.is_superuser)
        self.assertFalse(regular_user.is_staff)
