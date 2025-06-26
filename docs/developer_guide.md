# Glad Tidings School Management Portal - Developer Documentation

## Table of Contents
1. [Project Structure](#project-structure)
2. [Setting Up the Development Environment](#setting-up-the-development-environment)
3. [App Architecture](#app-architecture)
4. [Database Schema](#database-schema)
5. [Authentication and Authorization](#authentication-and-authorization)
6. [Key Features Implementation](#key-features-implementation)
7. [Testing](#testing)
8. [Deployment](#deployment)

## Project Structure

The project follows Django's standard structure with multiple apps for different functionality domains:

```
glad_tidings_school_mgmt/
├── academics/              # Academic-related functionality
├── accounting/             # Financial management
├── assignments/            # Student assignments
├── cbt/                    # Computer-based testing
├── core/                   # Core functionality and templates
├── docs/                   # Documentation
├── glad_school_portal/     # Main project settings
├── itsupport/              # IT support ticketing
├── staff/                  # Staff-specific functionality
├── students/               # Student-specific functionality
├── users/                  # Custom user model and authentication
├── .venv/                  # Virtual environment (not tracked in git)
├── manage.py               # Django management script
└── run_tests.sh            # Test runner script
```

## Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd glad_tidings_school_mgmt
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On Unix/MacOS
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create database migrations:
   ```bash
   python manage.py makemigrations
   ```

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## App Architecture

### Core App

The `core` app serves as the central hub for the application, containing:
- Base templates including the responsive layout
- Main views for landing pages and dashboards
- Notification system
- Public pages (landing, about us, admission)

### Users App

The `users` app handles user authentication and role-based access control:
- Custom user model with role field
- Role-based permissions
- Authentication views

### Academics App

The `academics` app manages educational content:
- Class timetables
- E-Library resources
- School calendar events
- Announcements

### Other Apps

- `students`: Student profiles and student-specific features
- `staff`: Staff profiles and staff-specific features
- `accounting`: Fee management and financial records
- `assignments`: Assignment creation, submission, and grading
- `cbt`: Computer-based testing system
- `itsupport`: Technical support ticket system

## Database Schema

### Core Models

#### UserNotification (core.models.UserNotification)
```python
class UserNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', db_index=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
```

### User Models

#### CustomUser (users.models.CustomUser)
```python
class CustomUser(AbstractUser):
    ROLES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
        ('it_support', 'IT Support'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='student')
```

### Academic Models

#### ClassTimetable (academics.models.ClassTimetable)
```python
class ClassTimetable(models.Model):
    class_name = models.CharField(max_length=50)
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    period = models.CharField(max_length=20)
    subject = models.CharField(max_length=100)
    teacher = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
```

#### ELibraryResource (academics.models.ELibraryResource)
```python
class ELibraryResource(models.Model):
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='other')
    subject = models.CharField(max_length=100, blank=True)
    grade_level = models.CharField(max_length=50, blank=True)
    file = models.FileField(upload_to='elibrary/')
    file_size = models.PositiveIntegerField(editable=False, null=True)
    download_count = models.PositiveIntegerField(default=0, editable=False)
```

#### Announcement (academics.models.Announcement)
```python
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    audience = models.CharField(max_length=10, choices=AUDIENCE_CHOICES, default='all')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    is_active = models.BooleanField(default=True)
    publish_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
```

### Student Models

#### StudentProfile (students.models.StudentProfile)
```python
class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=30, unique=True)
    date_of_birth = models.DateField()
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_contact = models.CharField(max_length=30, blank=True)
```

## Authentication and Authorization

### Custom User Model

The application uses a custom user model with role-based authentication:

1. The `CustomUser` model extends Django's `AbstractUser` with a `role` field
2. Roles determine which dashboard and features a user has access to
3. Role-based permissions are enforced in views with decorators and permission checks

### Login Flow

1. Users access the login page at `/accounts/login/`
2. After authentication, they are redirected to the dashboard view
3. The dashboard view checks the user's role and renders the appropriate template:
   - `dashboard_student.html` for students
   - `dashboard_staff.html` for staff
   - `dashboard_admin.html` for administrators
   - `dashboard_it.html` for IT support personnel

### Permission Decorators

Views that require authentication use Django's `@login_required` decorator. For role-specific views, additional checks are implemented in the view functions.

## Key Features Implementation

### Notification System

The notification system consists of:

1. A `UserNotification` model that stores user-specific notifications
2. Signal receivers that create notifications when announcements are created
3. Views to display, mark as read, and manage notifications
4. JavaScript to update notification badges in real-time

#### Creating Notifications

Notifications are automatically created from announcements:

```python
@receiver(post_save, sender=Announcement)
def create_notifications_from_announcement(sender, instance, created, **kwargs):
    if created and instance.is_active:
        UserNotification.create_from_announcement(instance)
```

#### Notification Views

The main notification view filters notifications based on user role and marks them as read:

```python
@login_required
def notifications(request):
    # Get announcements for the user's role
    # Get user-specific notifications
    # Handle mark as read functionality
    # Return rendered template
```

### Role-Based Dashboards

Each user role has a specific dashboard with tailored features:

```python
@login_required
def dashboard(request):
    user = request.user
    role = getattr(user, 'role', None)
    if role == 'student':
        return render(request, 'core/dashboard_student.html')
    elif role == 'staff':
        return render(request, 'core/dashboard_staff.html')
    # ... other roles
```

## Testing

### Test Categories

The project includes multiple test categories:

1. **URL Access Tests**: Verify URL accessibility based on user roles
2. **Security Tests**: Check authentication, CSRF protection, and secure headers
3. **Responsive Design Tests**: Verify mobile-first design principles
4. **Feature Module Tests**: Test specific feature modules
5. **Performance Tests**: Measure page load times
6. **Form Validation Tests**: Verify form validations
7. **API Tests**: Test API endpoints
8. **Mobile Tests**: Test mobile-specific functionality

### Running Tests

Use the `run_tests.sh` script to run tests:

```bash
# Run all tests
./run_tests.sh all-fixed

# Run specific test categories
./run_tests.sh [category]
```

## Deployment

### Production Settings

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Configure a proper database (PostgreSQL recommended)
3. Set `ALLOWED_HOSTS` to your domain
4. Use a secure `SECRET_KEY`
5. Set up static file serving with whitenoise or similar
6. Configure a proper email backend

### Deployment Options

1. **Traditional Hosting**:
   - Setup: Apache or Nginx + Gunicorn
   - Database: PostgreSQL
   - Static files: Served by web server or CDN

2. **Containerized Deployment**:
   - Docker containers for web and database
   - Docker Compose for local testing
   - Kubernetes for production scaling

3. **Platform as a Service (PaaS)**:
   - Heroku, PythonAnywhere, or similar
   - Automatic deployment from git repository

### Database Migration

When deploying database changes:

1. Create migrations locally:
   ```bash
   python manage.py makemigrations
   ```

2. Apply migrations in production:
   ```bash
   python manage.py migrate
   ```

### Static Files

In production, collect static files:

```bash
python manage.py collectstatic
```
