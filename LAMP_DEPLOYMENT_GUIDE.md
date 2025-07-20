# 🚀 LAMP Stack Deployment Guide

## Overview
This guide shows how to deploy the Glad Tidings School Management Portal on a LAMP (Linux, Apache, MySQL, Python) stack instead of the current Docker/PostgreSQL setup.

## 🔄 LAMP Stack Adaptation

### Current Architecture → LAMP Architecture
- **L**inux: Ubuntu/CentOS server
- **A**pache: Web server (replacing Nginx)
- **M**ySQL: Database (replacing PostgreSQL)  
- **P**ython: Django application (already Python-based)

## 📋 Prerequisites

### System Requirements
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y apache2 mysql-server mysql-client
sudo apt install -y libmysqlclient-dev python3-dev
sudo apt install -y libapache2-mod-wsgi-py3

# CentOS/RHEL
sudo yum install -y python3 python3-pip
sudo yum install -y httpd mysql-server mysql-devel
sudo yum install -y python3-mod_wsgi
```

## 🔧 Configuration Changes Required

### 1. Database Configuration
The project needs MySQL adapter instead of PostgreSQL:

#### Update requirements.txt
Remove:
```
psycopg2-binary  # PostgreSQL adapter
```

Add:
```
mysqlclient  # MySQL adapter for Django
PyMySQL  # Alternative MySQL adapter
```

#### Update settings.py
```python
# LAMP-specific database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env.str('DB_NAME', default='glad_school_db'),
        'USER': env.str('DB_USER', default='glad_user'),
        'PASSWORD': env.str('DB_PASSWORD', default='your_password'),
        'HOST': env.str('DB_HOST', default='localhost'),
        'PORT': env.str('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

### 2. Static Files Configuration
```python
# settings.py - LAMP static files
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/glad_school/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/glad_school/media/'

# Use WhiteNoise for static files in LAMP
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... other middleware
]

# Static files optimization
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## 🗄️ MySQL Database Setup

### 1. Create Database and User
```sql
-- Connect to MySQL as root
mysql -u root -p

-- Create database
CREATE DATABASE glad_school_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user and grant privileges
CREATE USER 'glad_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON glad_school_db.* TO 'glad_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 2. MySQL Configuration
```ini
# /etc/mysql/mysql.conf.d/mysqld.cnf
[mysqld]
# Performance optimizations
innodb_buffer_pool_size = 256M
max_connections = 200
query_cache_size = 32M
query_cache_type = 1

# Character set
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# File upload size (for bulk result uploads)
max_allowed_packet = 64M
```

## 🐍 Python Environment Setup

### 1. Create Virtual Environment
```bash
# Create project directory
sudo mkdir -p /var/www/glad_school
sudo chown -R $USER:www-data /var/www/glad_school
cd /var/www/glad_school

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (with MySQL adapter)
pip install -r requirements_lamp.txt
```

### 2. Environment Configuration
```bash
# Create .env file
cat > .env << EOF
DEBUG=False
SECRET_KEY=your_super_secret_key_here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,localhost

# MySQL Database
DB_NAME=glad_school_db
DB_USER=glad_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306

# Disable Redis for LAMP (use database sessions instead)
# REDIS_URL=redis://localhost:6379/1

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EOF
```

## 🌐 Apache Configuration

### 1. Virtual Host Configuration
```apache
# /etc/apache2/sites-available/glad_school.conf
<VirtualHost *:80>
    ServerName your-domain.com
    ServerAlias www.your-domain.com
    DocumentRoot /var/www/glad_school
    
    # WSGI Configuration
    WSGIDaemonProcess glad_school python-home=/var/www/glad_school/venv python-path=/var/www/glad_school
    WSGIProcessGroup glad_school
    WSGIScriptAlias / /var/www/glad_school/glad_school_portal/wsgi.py
    WSGIApplicationGroup %{GLOBAL}
    
    # Python path
    <Directory /var/www/glad_school/glad_school_portal>
        WSGIProcessGroup glad_school
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
    
    # Static files
    Alias /static /var/www/glad_school/static
    <Directory /var/www/glad_school/static>
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 1 year"
    </Directory>
    
    # Media files
    Alias /media /var/www/glad_school/media
    <Directory /var/www/glad_school/media>
        Require all granted
    </Directory>
    
    # Security headers
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    
    # Logging
    ErrorLog ${APACHE_LOG_DIR}/glad_school_error.log
    CustomLog ${APACHE_LOG_DIR}/glad_school_access.log combined
</VirtualHost>

# SSL Configuration (recommended)
<VirtualHost *:443>
    ServerName your-domain.com
    ServerAlias www.your-domain.com
    DocumentRoot /var/www/glad_school
    
    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /path/to/your/certificate.crt
    SSLCertificateKeyFile /path/to/your/private.key
    
    # Same WSGI and directory configuration as above
    # ... (repeat from HTTP configuration)
</VirtualHost>
```

### 2. Enable Site and Modules
```bash
# Enable required Apache modules
sudo a2enmod wsgi
sudo a2enmod rewrite
sudo a2enmod ssl
sudo a2enmod headers
sudo a2enmod expires

# Enable site
sudo a2ensite glad_school.conf
sudo a2dissite 000-default.conf

# Restart Apache
sudo systemctl restart apache2
```

## 🔄 Sessions Without Redis

Since LAMP typically doesn't include Redis, configure database sessions:

```python
# settings.py - Use database sessions instead of Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 hour

# Disable Redis cache, use database cache instead
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache',
    }
}

# Comment out Redis-specific settings
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': env('REDIS_URL', default='redis://localhost:6379/1'),
#     }
# }
```

## 🚀 Deployment Process

### 1. Upload Code and Setup
```bash
# Upload your project to /var/www/glad_school
# Ensure proper ownership
sudo chown -R www-data:www-data /var/www/glad_school
sudo chmod -R 755 /var/www/glad_school

# Activate virtual environment
cd /var/www/glad_school
source venv/bin/activate
```

### 2. Django Setup
```bash
# Install dependencies with MySQL support
pip install mysqlclient
pip install -r requirements.txt

# Create cache table (if using database cache)
python manage.py createcachetable

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Populate initial data
python manage.py loaddata initial_data.json  # if you have fixtures
# OR
python populate_classes_subjects.py
python create_test_users.py
```

### 3. Set Permissions
```bash
# Set proper permissions
sudo chown -R www-data:www-data /var/www/glad_school/media
sudo chown -R www-data:www-data /var/www/glad_school/static
sudo chmod -R 755 /var/www/glad_school/media
sudo chmod -R 755 /var/www/glad_school/static

# Database file permissions (if using SQLite for dev)
sudo chown www-data:www-data /var/www/glad_school/db.sqlite3
sudo chmod 644 /var/www/glad_school/db.sqlite3
```

## 🔒 Security Configuration

### 1. MySQL Security
```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Configure firewall
sudo ufw allow ssh
sudo ufw allow 'Apache Full'
sudo ufw allow mysql
sudo ufw enable
```

### 2. Django Security Settings
```python
# settings_production.py for LAMP
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Database connection security
DATABASES['default']['OPTIONS'].update({
    'sql_mode': 'traditional',
})
```

## 📊 Performance Optimization

### 1. Apache Optimization
```apache
# /etc/apache2/conf-available/performance.conf
# Enable compression
LoadModule deflate_module modules/mod_deflate.so
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>

# Enable caching
LoadModule expires_module modules/mod_expires.so
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpg "access plus 1 month"
    ExpiresByType image/jpeg "access plus 1 month"
    ExpiresByType image/gif "access plus 1 month"
    ExpiresByType image/png "access plus 1 month"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/pdf "access plus 1 month"
    ExpiresByType text/javascript "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>
```

### 2. MySQL Performance
```ini
# /etc/mysql/mysql.conf.d/performance.cnf
[mysqld]
# InnoDB settings
innodb_buffer_pool_size = 512M
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2

# Query cache
query_cache_type = 1
query_cache_size = 64M
query_cache_limit = 2M

# Connection settings
max_connections = 100
connect_timeout = 5
wait_timeout = 600
max_allowed_packet = 64M
thread_cache_size = 128
```

## 🔍 Monitoring and Maintenance

### 1. Log Monitoring
```bash
# Apache logs
sudo tail -f /var/log/apache2/glad_school_error.log
sudo tail -f /var/log/apache2/glad_school_access.log

# MySQL logs
sudo tail -f /var/log/mysql/error.log
```

### 2. Backup Scripts
```bash
#!/bin/bash
# backup_school.sh
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
mysqldump -u glad_user -p glad_school_db > /backups/db_backup_$DATE.sql

# Media files backup
tar -czf /backups/media_backup_$DATE.tar.gz /var/www/glad_school/media/

# Keep only last 7 days of backups
find /backups -name "*.sql" -mtime +7 -delete
find /backups -name "*.tar.gz" -mtime +7 -delete
```

## ✅ LAMP Deployment Checklist

- [ ] Linux server setup (Ubuntu/CentOS)
- [ ] Apache installation and configuration
- [ ] MySQL server installation and database creation
- [ ] Python environment setup with virtual environment
- [ ] MySQL adapter installation (mysqlclient)
- [ ] Django settings modification for MySQL
- [ ] Apache virtual host configuration
- [ ] SSL certificate installation (recommended)
- [ ] Static and media files configuration
- [ ] Database migrations and initial data
- [ ] Permissions and security setup
- [ ] Performance optimization
- [ ] Monitoring and backup setup

## 🎯 Benefits of LAMP Deployment

### Advantages:
1. **Familiar Stack**: Many hosting providers support LAMP
2. **Cost-effective**: Shared hosting options available
3. **Mature Ecosystem**: Well-documented and supported
4. **Performance**: Apache + MySQL can handle high traffic
5. **Security**: Well-established security practices

### Considerations:
1. **Redis Features**: Some caching features may need adaptation
2. **PostgreSQL Features**: MySQL has different JSON handling
3. **Docker Benefits**: Lose containerization advantages
4. **Scaling**: May need additional configuration for horizontal scaling

## 🚀 Next Steps

1. **Test Deployment**: Set up on a test server first
2. **Performance Testing**: Load test with school data
3. **Security Audit**: Review security configurations
4. **Backup Strategy**: Implement regular backup procedures
5. **Monitoring Setup**: Configure system monitoring
6. **Documentation**: Update deployment documentation

The Glad Tidings School Management Portal can absolutely run on LAMP stack with these modifications. The core Django application architecture remains the same, with only infrastructure and database adapter changes required.
