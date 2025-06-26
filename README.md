# Glad Tidings School Management Portal

A comprehensive school management system built with Django, featuring role-based dashboards for students, staff, administrators, and IT support personnel.

## Features

- **Role-Based Access Control**: Separate dashboards and permissions for students, staff, administrators, and IT support
- **Academic Management**: Course materials, timetables, assignments, and grades
- **Student Management**: Profiles, attendance, performance tracking
- **Staff Management**: Profiles, attendance, teaching assignments
- **Financial Management**: Fee tracking, payments, financial reports
- **Notification System**: School-wide announcements and personalized notifications
- **E-Library**: Digital resources for students and staff
- **Computer-Based Testing (CBT)**: Online assessment platform
- **Mobile-First Design**: Fully responsive interface for all devices

## Screenshots

![Dashboard](docs/images/dashboard.png)
![Notifications](docs/images/notifications.png)

## Documentation

- [User Guide](docs/user_guide.md): Complete guide for all users
- [Developer Guide](docs/developer_guide.md): Technical documentation for developers
- [Adding Users Guide](docs/adding_users_guide.md): Quick reference for user management

## Technologies Used

- **Backend**: Django 5.2.3, Python 3.13.5
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Django Authentication System
- **Testing**: Django Test Framework

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/idorenyinbassey/glad_school_mgm.git
   cd glad_school_mgm
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

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at: http://127.0.0.1:8000/

## Running Tests

Use the provided test runner script:

```bash
./run_tests.sh all-fixed
```

Or for specific test categories:

```bash
./run_tests.sh [category]
```

Where category is one of: url, security, responsive, features, performance, forms, mobile, api

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Django Framework
- Bootstrap
- FontAwesome
- The Glad Tidings School community
