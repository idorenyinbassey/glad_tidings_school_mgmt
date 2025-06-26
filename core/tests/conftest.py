import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def create_admin_user():
    """Fixture to create and return an admin user"""
    admin = User.objects.create_user(
        username="admin_fixture",
        email="admin_fixture@example.com",
        password="adminpass123",
        role="admin"
    )
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    return admin

@pytest.fixture
def create_staff_user():
    """Fixture to create and return a staff user"""
    staff = User.objects.create_user(
        username="staff_fixture",
        email="staff_fixture@example.com",
        password="staffpass123",
        role="staff"
    )
    staff.save()
    return staff

@pytest.fixture
def create_student_user():
    """Fixture to create and return a student user"""
    student = User.objects.create_user(
        username="student_fixture",
        email="student_fixture@example.com",
        password="studentpass123",
        role="student"
    )
    student.save()
    return student
