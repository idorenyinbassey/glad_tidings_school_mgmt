# Glad Tidings School Management Portal

[![Django CI/CD Pipeline](https://github.com/idorenyinbassey/glad_school_mgm/actions/workflows/django-ci.yml/badge.svg)](https://github.com/idorenyinbassey/glad_school_mgm/actions/workflows/django-ci.yml)

A comprehensive school management system built with Django, featuring role-based dashboards for students, staff, administrators, and IT support personnel.

## Features

- **Role-Based Access Control**: Separate dashboards and permissions for students, staff, administrators, accountants, and IT support
- **Academic Management**: Course materials, timetables, assignments, and grades
- **Student Management**: Profiles, attendance, performance tracking
- **Staff Management**: Profiles, attendance, teaching assignments
- **Complete Result Management System**: 
  - Individual and bulk CSV result entry for all assessment types
  - Automated result compilation with weighted grade calculation
  - Professional PDF result sheets with school branding
  - Live student portal for result viewing and printing
  - Real-time result access for students with color-coded performance indicators
  - Support for 30 classes (JSS1A-E to SS3A-E) and 50+ subjects
  - Teacher remarks and comprehensive feedback system
- **Professional Finance Module**: 
  - Comprehensive fee management and tracking
  - Payment processing and recording
  - Expense management and payroll
  - Real-time financial metrics and analytics
  - Interactive charts and financial trends
  - Professional accountant dashboard
- **Notification System**: School-wide announcements and personalized notifications
- **E-Library**: Digital resources for students and staff
- **Computer-Based Testing (CBT)**: Online assessment platform
- **Mobile-First Design**: Fully responsive interface for all devices
- **Multiple Deployment Options**: 🐳 Docker containerization or 🌐 Traditional LAMP stack
- **Production-Ready**: Clean code, zero linting errors, optimized performance

## Screenshots

![Dashboard](docs/images/dashboard.png)
![Notifications](docs/images/notifications.png)

## Documentation

- [LAMP Deployment Guide](LAMP_DEPLOYMENT_GUIDE.md): 🌐 **NEW** - Complete LAMP stack deployment guide
- [Docker Guide](docs/DOCKER_GUIDE.md): 🐳 Complete Docker deployment guide (Recommended)
- [Installation Guide](docs/INSTALLATION.md): Comprehensive setup instructions
- [User Guide](docs/user_guide.md): Complete guide for all users
- [Result Management Guide](docs/COMPLETE_USER_GUIDE.md): 📊 Complete result management system documentation
- [Accounting & Finance Guide](docs/accounting_finance_guide.md): 💰 Comprehensive finance module documentation
- [Developer Guide](docs/developer_guide.md): Technical documentation for developers
- [Adding Users Guide](docs/adding_users_guide.md): Quick reference for user management
- [API Documentation](docs/API_DOCUMENTATION.md): 📡 Technical API reference for result management
- [Development History](docs/DEVELOPMENT_HISTORY.md): 🚀 Complete development journey and technical details
- [Security & Performance](docs/security_performance.md): Security features and optimizations
- [Superuser Roles](docs/superuser_roles.md): Guide for managing superuser roles
- [User Model Fixes](docs/user_model_fixes.md): Documentation about fixes to the user model and manager

## Technologies Used

- **Backend**: Django 5.2, Python 3.9+
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Django Authentication System with Two-Factor Auth
- **Caching**: Redis for performance optimization
- **Testing**: Django Test Framework, pytest
- **Deployment**: 🐳 Docker & Docker Compose, 🌐 LAMP Stack, Nginx, Gunicorn
- **CI/CD**: GitHub Actions

## Quick Start

🚀 **Choose Your Deployment Method**

### 🐳 **Docker Deployment (Recommended)**

For the easiest deployment, use Docker:

```bash
# Clone repository
git clone https://github.com/idorenyinbassey/glad_tidings_school_mgmt.git
cd glad_tidings_school_mgmt

# Interactive deployment script
./docker_deploy.sh

# Or manual deployment
# Development mode
docker-compose -f docker-compose.dev.yml up --build -d

# Production mode (configure .env first)
cp .env.docker .env  # Edit with your values
docker-compose up --build -d
```

**Access Points:**
- Development: http://localhost:8000
- Production: http://localhost
- Admin: http://localhost/admin

See the [Docker Guide](docs/DOCKER_GUIDE.md) for detailed Docker deployment instructions.

### 🌐 **LAMP Stack Deployment**

For deployment on traditional LAMP hosting (shared hosting, VPS):

```bash
# Clone repository
git clone https://github.com/idorenyinbassey/glad_tidings_school_mgmt.git
cd glad_tidings_school_mgmt

# Automated LAMP deployment (Ubuntu/CentOS)
chmod +x deploy_lamp.sh
./deploy_lamp.sh

# Manual LAMP setup
pip install -r requirements_lamp.txt
# Configure Apache and MySQL (see LAMP guide)
```

**LAMP Access Points:**
- Web Interface: http://your-domain.com/
- Admin Panel: http://your-domain.com/admin/

See the [LAMP Deployment Guide](LAMP_DEPLOYMENT_GUIDE.md) for detailed LAMP stack deployment instructions.

### 🖥️ **Traditional Development Installation**

For detailed installation instructions, see the [Installation Guide](docs/INSTALLATION.md).

```bash
# Clone repository
git clone https://github.com/idorenyinbassey/glad_tidings_school_mgmt.git
cd glad_tidings_school_mgmt

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Set up database
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Access the application at: http://127.0.0.1:8000/

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

## Continuous Integration/Continuous Deployment

This project uses GitHub Actions for CI/CD:

- Automated testing on every push and pull request
- Code linting and style checks
- Test coverage reporting
- Automated builds
- Deployment pipeline (when configured)

The workflow configuration can be found in `.github/workflows/django-ci.yml`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Django Framework
- Bootstrap
- FontAwesome
- The Glad Tidings School community
