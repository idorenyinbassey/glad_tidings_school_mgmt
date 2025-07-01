# 🚀 Production Deployment Checklist

## Pre-Deployment Verification

### ✅ Security Checks
- [ ] Django Debug Toolbar completely removed
- [ ] DEBUG = False in production settings
- [ ] SECRET_KEY set from environment variable
- [ ] ALLOWED_HOSTS configured properly
- [ ] CSRF and security middleware enabled
- [ ] HTTPS redirect configured
- [ ] Secure cookies enabled

### ✅ Database Setup
- [ ] Production database configured (PostgreSQL/MySQL)
- [ ] Database migrations applied
- [ ] Initial data loaded (superuser, sample data)
- [ ] Database backups configured
- [ ] Connection pooling enabled

### ✅ Static Files & Media
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Media files directory configured
- [ ] WhiteNoise or CDN configured for static files
- [ ] File permissions set correctly

### ✅ Environment Configuration
- [ ] Environment variables file created (.env)
- [ ] All sensitive data moved to environment variables
- [ ] Production-specific settings enabled
- [ ] Logging configuration verified

## Deployment Steps

### 1. Server Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install python3 python3-pip python3-venv nginx postgresql redis-server -y

# Create application user
sudo useradd --system --create-home gladschool
```

### 2. Application Setup
```bash
# Switch to application user
sudo su - gladschool

# Clone repository
git clone <repository_url> glad_school_portal
cd glad_school_portal

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Configuration
```bash
# Create PostgreSQL database and user
sudo -u postgres psql
CREATE DATABASE gladschool_db;
CREATE USER gladschool_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE gladschool_db TO gladschool_user;
\q

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

### 4. Web Server Setup (Nginx + Gunicorn)
```bash
# Install Gunicorn
pip install gunicorn

# Create Gunicorn service file
sudo nano /etc/systemd/system/gladschool.service
```

**Gunicorn Service Configuration:**
```ini
[Unit]
Description=Glad Tidings School Management
After=network.target

[Service]
User=gladschool
Group=gladschool
WorkingDirectory=/home/gladschool/glad_school_portal
Environment="PATH=/home/gladschool/glad_school_portal/venv/bin"
ExecStart=/home/gladschool/glad_school_portal/venv/bin/gunicorn --workers 3 --bind unix:/home/gladschool/glad_school_portal/gladschool.sock glad_school_portal.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/gladschool/glad_school_portal;
    }
    
    location /media/ {
        root /home/gladschool/glad_school_portal;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/gladschool/glad_school_portal/gladschool.sock;
    }
}
```

### 5. SSL Configuration (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

### 6. Service Management
```bash
# Start and enable services
sudo systemctl start gladschool
sudo systemctl enable gladschool
sudo systemctl restart nginx
sudo systemctl enable nginx

# Check service status
sudo systemctl status gladschool
sudo systemctl status nginx
```

## Post-Deployment Verification

### ✅ Application Health Checks
- [ ] Website loads correctly (HTTP/HTTPS)
- [ ] Admin panel accessible
- [ ] User authentication working
- [ ] Dashboard displays data correctly
- [ ] Charts and AJAX functionality working
- [ ] File uploads working (if applicable)

### ✅ Performance Checks
- [ ] Page load times acceptable (<3 seconds)
- [ ] Database queries optimized
- [ ] Static files served correctly
- [ ] No JavaScript errors in console
- [ ] Mobile responsive design working

### ✅ Security Verification
- [ ] HTTPS enforced
- [ ] Security headers present
- [ ] Admin panel secured
- [ ] No debug information exposed
- [ ] File permissions correct

### ✅ Monitoring Setup
- [ ] Log files configured and rotating
- [ ] Error monitoring enabled
- [ ] Backup procedures tested
- [ ] Health check endpoints working
- [ ] Performance monitoring enabled

## Environment Variables Template (.env)

```bash
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database Configuration
DATABASE_URL=postgresql://gladschool_user:password@localhost:5432/gladschool_db

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# Cache Configuration
REDIS_URL=redis://localhost:6379/1

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Troubleshooting Common Issues

### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test database connection
python manage.py dbshell
```

### Static Files Not Loading
```bash
# Recollect static files
python manage.py collectstatic --clear --noinput

# Check Nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

### Permission Errors
```bash
# Fix ownership
sudo chown -R gladschool:gladschool /home/gladschool/glad_school_portal

# Fix permissions
chmod 755 /home/gladschool/glad_school_portal
```

## Maintenance Commands

### Regular Maintenance
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
sudo systemctl restart gladschool
```

### Database Backup
```bash
# Create backup
pg_dump gladschool_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql gladschool_db < backup_file.sql
```

---

**🎉 Your Glad Tidings School Management System is now production-ready!**
