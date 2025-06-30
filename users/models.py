from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
import string
import random

# Create a custom manager to handle superuser creation properly
class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        # Ensure role is set to 'admin' for superusers
        extra_fields.setdefault('role', 'admin')
        return super().create_superuser(username, email, password, **extra_fields)
        
    def make_random_password(self, length=10, allowed_chars=string.ascii_letters + string.digits + string.punctuation):
        """
        Generate a random password with the given length and allowed characters.
        This reimplements the method from Django's BaseUserManager.
        """
        return ''.join(random.choice(allowed_chars) for i in range(length))

# Create your models here.

class CustomUser(AbstractUser):
    ROLES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
        ('accountant', 'Accountant'),
        ('it_support', 'IT Support'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='student')
    # Add more custom fields as needed (e.g., phone, address, etc.)
    
    # Use the custom manager
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
