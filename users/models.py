from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    ROLES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
        ('it_support', 'IT Support'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='student')
    # Add more custom fields as needed (e.g., phone, address, etc.)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
