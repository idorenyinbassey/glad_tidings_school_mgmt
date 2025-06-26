import pytest
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

# Session fixture for database setup/teardown
@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up the test database once for the test session"""
    with django_db_blocker.unblock():
        # You could load initial data here if needed
        pass
    yield
    # Any session-level cleanup could go here

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

@pytest.fixture
def authenticated_client(client, create_admin_user):
    """Returns an authenticated client with an admin user"""
    client.login(username="admin_fixture", password="adminpass123")
    return client

@pytest.fixture
def authenticated_staff_client(client, create_staff_user):
    """Returns an authenticated client with a staff user"""
    client.login(username="staff_fixture", password="staffpass123")
    return client

@pytest.fixture
def authenticated_student_client(client, create_student_user):
    """Returns an authenticated client with a student user"""
    client.login(username="student_fixture", password="studentpass123")
    return client
