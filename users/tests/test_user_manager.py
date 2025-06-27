from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import CustomUser

class UserManagerTests(TestCase):
    def test_create_superuser(self):
        """Test that superusers are created with the 'admin' role by default"""
        User = get_user_model()
        
        admin_user = User.objects.create_superuser(
            username="testadmin",
            email="admin@example.com",
            password="adminpassword"
        )
        
        self.assertEqual(admin_user.role, "admin")
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
    
    def test_make_random_password(self):
        """Test that the make_random_password method works in our custom manager"""
        User = get_user_model()
        
        # Generate a random password
        password = User.objects.make_random_password(length=12)
        
        # Check that it's a string of the right length
        self.assertIsInstance(password, str)
        self.assertEqual(len(password), 12)
