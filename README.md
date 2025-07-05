# 🏫 Glad Tidings School Management Portal

[![Django CI/CD Pipeline](https://github.com/idorenyinbassey/glad_school_mgm/actions/workflows/django-ci.yml/badge.svg)](https://github.com/idorenyinbassey/glad_school_mgm/actions/workflows/django-ci.yml)
[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-success)](.)
[![Live Result System](https://img.shields.io/badge/Features-Live%20Result%20Management-blue)](.)

A comprehensive school management system built with Django, featuring a complete live result management system, user role management, accounting, and advanced academic tracking. **Production-ready with full functionality and zero placeholders.**

## ✨ Features

### 🎓 Complete Live Result Management System
- **Real-Time Result Entry**: Individual and bulk CSV upload for student assessments
- **Automated Result Compilation**: Weighted grade calculation and class ranking
- **Live Student Portal**: Real-time result viewing with filtering and PDF export
- **Professional Result Sheets**: Printable PDF result sheets with school branding
- **Comprehensive Feedback**: Teacher remarks and performance analytics
- **Assessment Framework**: CA1 (15%), CA2 (15%), CA3 (20%), Exam (50%), plus assignments and projects
- **30 Classes Supported**: JSS1A-E through SS3A-E with 50+ subjects
- **Zero Placeholders**: All functionality is live and operational

### 👥 Multi-Role Access Control
- **Admin Dashboard**: Complete system oversight with result management access
- **Staff Dashboard**: Result entry, bulk upload, compilation, and student management
- **Student Dashboard**: Live result viewing, filtering, and professional PDF printing
- **Role-Based Security**: Granular permissions with secure authentication
- **Real-Time Data**: All dashboards display live database information

### 🏫 Academic Management Excellence
- **Academic Framework**: Complete session and term management (2024/2025 academic year)
- **Class Structure**: 30 active classes (JSS1A-E, JSS2A-E, JSS3A-E, SS1A-E, SS2A-E, SS3A-E)
- **Comprehensive Curriculum**: Core, Science, Arts, and Commercial subject streams
- **Performance Analytics**: Live statistics, grade distribution, and class rankings
- **Advanced Filtering**: Session, term, and subject-based result filtering

### � Advanced Features & Integration
- **Live Data Integration**: Real-time dashboards with actual database queries
- **Professional PDF Generation**: High-quality result sheets using ReportLab
- **Bulk Operations**: Efficient CSV upload with comprehensive validation
- **Advanced Analytics**: Performance tracking, statistics, and grade distribution
- **AJAX-Powered Interface**: Dynamic content loading and real-time updates
- **Mobile-First Design**: Responsive interface optimized for all devices
- **Security-First**: Role-based permissions and comprehensive input validation

### 🎯 Educational Excellence Features
- **Immediate Result Access**: Students view results as soon as teachers enter them
- **Performance Tracking**: Color-coded indicators and trend analysis
- **Comprehensive Reporting**: Individual, class, and subject-level analytics
- **Professional Documentation**: Printable result sheets for parents and records
- **Teacher Efficiency**: Streamlined entry process with bulk upload capabilities
- **Data Integrity**: Automated validation and error prevention

## 📈 System Statistics
- **8 Core Models**: Complete academic data structure
- **30 Active Classes**: JSS1A-E through SS3A-E
- **50+ Subjects**: Full curriculum coverage across all streams
- **6 Assessment Types**: Comprehensive evaluation framework
- **Zero Placeholders**: 100% live, functional system

## Screenshots

![Dashboard](docs/images/dashboard.png)
![Notifications](docs/images/notifications.png)

## Documentation

- [📋 Complete User Guide](docs/COMPLETE_USER_GUIDE.md): Comprehensive guide for all users and roles
- [🚀 Development History](docs/DEVELOPMENT_HISTORY.md): Complete development journey and technical details
- [📡 API Documentation](docs/API_DOCUMENTATION.md): Technical API reference and integration guide
- [🎉 Project Completion Report](FINAL_PROJECT_COMPLETION.md): Comprehensive completion summary
- [🐳 Docker Guide](docs/DOCKER_GUIDE.md): Complete Docker deployment guide (if available)
- [⚡ Quick Start Guide](docs/INSTALLATION.md): Setup and installation instructions

## Technologies Used

- **Backend**: Django 5.2, Python 3.9+
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Django Authentication System with Two-Factor Auth
- **Caching**: Redis for performance optimization
- **Testing**: Django Test Framework, pytest
- **Deployment**: 🐳 Docker & Docker Compose, Nginx, Gunicorn
- **CI/CD**: GitHub Actions

## Quick Start

🐳 **Docker Deployment (Recommended)**

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
- **Main Portal**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Result Management**: http://localhost:8000/results/ (Staff/Admin)
- **Student Results**: http://localhost:8000/students/results/ (Students)
- **API Endpoints**: Full REST API for result management integration

See the [Docker Guide](docs/DOCKER_GUIDE.md) for detailed Docker deployment instructions.

🖥️ **Traditional Installation**

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
