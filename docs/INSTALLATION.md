# Glad Tidings School Management Portal - Installation Guide

This guide provides comprehensive instructions for setting up the Glad Tidings School Management Portal on your system. Follow these steps for both development and production environments.

## Prerequisites

- **Python**: Version 3.9 or higher
- **Git**: For cloning the repository
- **Redis** (optional): For caching and performance optimization
- **PostgreSQL** (recommended for production): Database server
- **Virtual Environment**: For isolated dependencies

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/idorenyinbassey/glad_tidings_school_mgmt.git
cd glad_tidings_school_mgmt
```

### 2. Set Up a Virtual Environment

```bash
# Create a new virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

The project uses a flexible requirements approach without strict version pinning to allow for compatible updates:

```bash
pip install -r requirements.txt
```

> **Note**: If you need to create a locked environment with exact versions, you can run `pip freeze > requirements-locked.txt` after installation.

### 4. Configure Environment Variables

```bash
# Create .env file from example
cp .env.example .env
```

Edit the `.env` file with your specific settings:

- Set your `SECRET_KEY` (generate a new one for security)
- Configure `ALLOWED_HOSTS` for your environment
- Set up database connection
- Configure email settings for notifications
- Add Redis URL if using caching

### 5. Database Setup

```bash
# Create database migrations (if needed)
python manage.py makemigrations

# Apply migrations to set up the database schema
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user with full access to the system.

### 7. Static Files

```bash
# Collect static files (required for production)
python manage.py collectstatic
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

The server will be available at http://127.0.0.1:8000/

## Production Deployment 

For production environments, additional setup is recommended:

### Using WSGI with Gunicorn

```bash
# Install Gunicorn if not included in requirements
pip install gunicorn

# Run with Gunicorn
gunicorn glad_school_portal.wsgi:application --bind 0.0.0.0:8000
```

### Security Considerations

For production deployments, update your `.env` file with secure settings:

```
DEBUG=False
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

### Setting Up Redis Cache (Optional)

If you want to use Redis for caching:

1. Ensure Redis is installed and running on your server
2. Set the `REDIS_URL` in your `.env` file
3. The Django settings are already configured to use Redis when available

## Troubleshooting

### Common Issues

1. **Migration Errors**: If you encounter migration issues, try:
   ```bash
   python manage.py migrate --fake-initial
   ```

2. **Static Files Not Loading**: Make sure you've run `collectstatic` and properly configured your web server to serve static files.

3. **Environment Variables Not Loading**: Ensure `.env` file is in the correct location and properly formatted.

### Getting Help

If you encounter issues not covered here, please:

1. Check the [developer documentation](docs/developer_guide.md)
2. Open an issue on GitHub
3. Contact the development team at the email listed in the project README

## Next Steps

Once installation is complete:

1. Visit the admin interface at `/admin/` to configure system settings
2. Create initial user accounts for different roles
3. Set up academic records, courses, and student information
4. Explore the documentation for specific feature usage
