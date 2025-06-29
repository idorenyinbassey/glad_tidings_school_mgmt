# Production Deployment and Maintenance Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Production Deployment](#production-deployment)
4. [Security Configuration](#security-configuration)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Backup and Recovery](#backup-and-recovery)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04 LTS or newer (recommended)
- **Python**: 3.9 or higher
- **Database**: PostgreSQL 12+ (recommended) or MySQL 8.0+
- **Cache**: Redis 6.0+
- **Web Server**: Nginx 1.18+
- **Process Manager**: Systemd or Supervisor
- **SSL Certificate**: Valid SSL certificate for HTTPS

### Hardware Requirements
- **Minimum**: 2 CPU cores, 4GB RAM, 20GB storage
- **Recommended**: 4+ CPU cores, 8GB+ RAM, 50GB+ SSD storage
- **Production**: 8+ CPU cores, 16GB+ RAM, 100GB+ SSD storage

## Environment Setup

### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    git \
    supervisor \
    fail2ban \
    ufw \
    certbot \
    python3-certbot-nginx

# Create application user
sudo adduser --disabled-password --gecos '' gladschool
sudo usermod -aG sudo gladschool
```

### 2. Database Setup
```bash
# Switch to postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE glad_school_db;
CREATE USER glad_school_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE glad_school_db TO glad_school_user;
ALTER USER glad_school_user CREATEDB;  -- For running tests
\q

# Configure PostgreSQL for production
sudo nano /etc/postgresql/*/main/postgresql.conf
# Uncomment and modify:
# shared_preload_libraries = 'pg_stat_statements'
# max_connections = 100
# shared_buffers = 256MB
# effective_cache_size = 1GB
# work_mem = 4MB
# maintenance_work_mem = 64MB

sudo systemctl restart postgresql
```

### 3. Redis Configuration
```bash
# Configure Redis for production
sudo nano /etc/redis/redis.conf

# Modify these settings:
# maxmemory 256mb
# maxmemory-policy allkeys-lru
# save 900 1
# save 300 10
# requirepass your_redis_password

sudo systemctl restart redis-server
```

## Production Deployment

### 1. Code Deployment
```bash
# Switch to application user
sudo su - gladschool

# Clone repository
git clone https://github.com/yourusername/glad_tidings_school_mgmt.git
cd glad_tidings_school_mgmt

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create production environment file
cp .env.production.example .env.production
nano .env.production
```

### 2. Environment Configuration
Edit `.env.production` with your production values:
```bash
SECRET_KEY=your-super-secret-production-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

DATABASE_URL=postgresql://glad_school_user:your_secure_password@localhost:5432/glad_school_db

REDIS_URL=redis://:your_redis_password@localhost:6379/1

EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
SERVER_EMAIL=admin@yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

STATIC_ROOT=/var/www/glad_school/staticfiles
MEDIA_ROOT=/var/www/glad_school/media
```

### 3. Database and Static Files
```bash
# Run migrations
python manage.py migrate --settings=glad_school_portal.settings_production

# Create superuser
python manage.py createsuperuser --settings=glad_school_portal.settings_production

# Collect static files
sudo mkdir -p /var/www/glad_school/staticfiles
sudo mkdir -p /var/www/glad_school/media
sudo chown -R gladschool:gladschool /var/www/glad_school/
python manage.py collectstatic --noinput --settings=glad_school_portal.settings_production
```

### 4. Gunicorn Configuration
Create Gunicorn configuration file:
```bash
nano /home/gladschool/glad_tidings_school_mgmt/gunicorn.conf.py
```

```python
# gunicorn.conf.py
bind = "unix:/home/gladschool/glad_tidings_school_mgmt/glad_school.sock"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "gladschool"
group = "gladschool"
tmp_upload_dir = None
logfile = "/home/gladschool/glad_tidings_school_mgmt/logs/gunicorn.log"
loglevel = "info"
access_logfile = "/home/gladschool/glad_tidings_school_mgmt/logs/gunicorn_access.log"
error_logfile = "/home/gladschool/glad_tidings_school_mgmt/logs/gunicorn_error.log"
```

### 5. Systemd Service
Create systemd service file:
```bash
sudo nano /etc/systemd/system/glad-school.service
```

```ini
[Unit]
Description=Glad Tidings School Management System
After=network.target

[Service]
Type=notify
User=gladschool
Group=gladschool
WorkingDirectory=/home/gladschool/glad_tidings_school_mgmt
Environment=PATH=/home/gladschool/glad_tidings_school_mgmt/venv/bin
Environment=DJANGO_SETTINGS_MODULE=glad_school_portal.settings_production
ExecStart=/home/gladschool/glad_tidings_school_mgmt/venv/bin/gunicorn --config gunicorn.conf.py glad_school_portal.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable glad-school
sudo systemctl start glad-school
sudo systemctl status glad-school
```

### 6. Nginx Configuration
Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/glad-school
```

```nginx
upstream glad_school_app {
    server unix:/home/gladschool/glad_tidings_school_mgmt/glad_school.sock;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://code.jquery.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self';" always;

    client_max_body_size 5M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        root /var/www/glad_school;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
    }
    
    location /media/ {
        root /var/www/glad_school;
        expires 1y;
        add_header Cache-Control "public";
    }

    location / {
        include proxy_params;
        proxy_pass http://glad_school_app;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        
        # Rate limiting
        limit_req zone=general burst=20 nodelay;
    }
    
    # Admin section with additional security
    location /admin/ {
        include proxy_params;
        proxy_pass http://glad_school_app;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        
        # Stricter rate limiting for admin
        limit_req zone=admin burst=5 nodelay;
        
        # Additional security for admin
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
    }
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=admin:10m rate=1r/s;
```

```bash
# Enable site and restart Nginx
sudo ln -s /etc/nginx/sites-available/glad-school /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL Certificate
```bash
# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Security Configuration

### 1. Firewall Setup
```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Fail2Ban Configuration
```bash
# Configure Fail2Ban for Django
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
maxretry = 10
findtime = 600
bantime = 7200
```

```bash
sudo systemctl restart fail2ban
```

### 3. Regular Security Updates
Create automated security update script:
```bash
sudo nano /etc/cron.daily/security-updates
```

```bash
#!/bin/bash
apt update
apt upgrade -y --only-upgrade $(apt list --upgradable 2>/dev/null | grep -i security | cut -d/ -f1)
```

```bash
sudo chmod +x /etc/cron.daily/security-updates
```

## Monitoring and Maintenance

### 1. Health Monitoring
Create monitoring script:
```bash
nano /home/gladschool/monitor.sh
```

```bash
#!/bin/bash
cd /home/gladschool/glad_tidings_school_mgmt
source venv/bin/activate

# Run health checks
python manage.py health_monitor --send-alerts --settings=glad_school_portal.settings_production

# Generate performance report
python manage.py performance_report --hours=24 --settings=glad_school_portal.settings_production

# Security audit (weekly)
if [ $(date +%u) -eq 1 ]; then  # Monday
    python manage.py security_audit --send-alerts --settings=glad_school_portal.settings_production
fi
```

```bash
chmod +x /home/gladschool/monitor.sh

# Add to crontab
crontab -e
# Add: 0 */4 * * * /home/gladschool/monitor.sh
```

### 2. Log Rotation
```bash
sudo nano /etc/logrotate.d/glad-school
```

```
/home/gladschool/glad_tidings_school_mgmt/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 gladschool gladschool
    postrotate
        systemctl reload glad-school
    endscript
}
```

### 3. Performance Monitoring
Set up automated performance monitoring:
```bash
# Create performance monitoring script
nano /home/gladschool/performance_check.py
```

```python
#!/usr/bin/env python3
import os
import django
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings_production')
django.setup()

from core.performance import PerformanceAnalyzer

# Get performance summary
summary = PerformanceAnalyzer.get_performance_summary(hours=1)

# Check for issues
issues = []
if summary.get('avg_response_time', 0) > 2.0:
    issues.append(f"High average response time: {summary['avg_response_time']:.2f}s")

if summary.get('error_rate', 0) > 5.0:
    issues.append(f"High error rate: {summary['error_rate']:.2f}%")

if issues:
    # Send alert (implement your alerting mechanism)
    print(f"Performance issues detected: {', '.join(issues)}")
    
# Log performance data
with open('/home/gladschool/logs/performance.log', 'a') as f:
    f.write(f"{datetime.now().isoformat()}: {json.dumps(summary)}\n")
```

## Backup and Recovery

### 1. Database Backup
Create backup script:
```bash
nano /home/gladschool/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/glad_school"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -h localhost -U glad_school_user glad_school_db | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Media files backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C /var/www/glad_school media/

# Application backup (excluding venv and __pycache__)
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz \
    --exclude="venv" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    -C /home/gladschool glad_tidings_school_mgmt/

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.gz" -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x /home/gladschool/backup.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /home/gladschool/backup.sh
```

### 2. Recovery Procedures
```bash
# Database recovery
gunzip -c /var/backups/glad_school/db_backup_YYYYMMDD_HHMMSS.sql.gz | psql -h localhost -U glad_school_user glad_school_db

# Media files recovery
tar -xzf /var/backups/glad_school/media_backup_YYYYMMDD_HHMMSS.tar.gz -C /var/www/glad_school/

# Application recovery
tar -xzf /var/backups/glad_school/app_backup_YYYYMMDD_HHMMSS.tar.gz -C /home/gladschool/
```

## Performance Optimization

### 1. Database Optimization
```sql
-- PostgreSQL optimizations
CREATE INDEX CONCURRENTLY idx_students_created_at ON students_studentprofile(created_at);
CREATE INDEX CONCURRENTLY idx_core_notifications_read ON core_notification(is_read, recipient_id);

-- Analyze tables
ANALYZE;

-- Check for unused indexes
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats 
WHERE schemaname = 'public' 
ORDER BY n_distinct DESC;
```

### 2. Cache Optimization
```python
# Redis optimization commands
# redis-cli
CONFIG SET maxmemory-policy allkeys-lru
CONFIG SET timeout 300
```

### 3. Application Optimization
```bash
# Enable Django template caching
# Already configured in settings_production.py

# Use database connection pooling
pip install django-db-pool
# Configure in settings
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Application Won't Start
```bash
# Check service status
sudo systemctl status glad-school

# Check logs
sudo journalctl -u glad-school -f

# Check Gunicorn logs
tail -f /home/gladschool/glad_tidings_school_mgmt/logs/gunicorn_error.log
```

#### 2. Database Connection Issues
```bash
# Test database connection
sudo -u gladschool psql -h localhost -U glad_school_user glad_school_db

# Check PostgreSQL status
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*-main.log
```

#### 3. Static Files Not Loading
```bash
# Check static files collection
cd /home/gladschool/glad_tidings_school_mgmt
source venv/bin/activate
python manage.py collectstatic --settings=glad_school_portal.settings_production

# Check file permissions
ls -la /var/www/glad_school/staticfiles/
```

#### 4. High Memory Usage
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Check for memory leaks in application
python manage.py performance_report --hours=1 --settings=glad_school_portal.settings_production
```

#### 5. Slow Performance
```bash
# Check database performance
python manage.py dbshell --settings=glad_school_portal.settings_production
# Run: SELECT * FROM pg_stat_activity WHERE state = 'active';

# Check Redis performance
redis-cli
# Run: INFO stats
```

### Emergency Procedures

#### 1. Service Recovery
```bash
# Quick service restart
sudo systemctl restart glad-school nginx

# Full system recovery
sudo systemctl restart postgresql redis-server nginx glad-school
```

#### 2. Database Recovery
```bash
# Restore from latest backup
/home/gladschool/backup.sh  # Create current backup first
# Then restore from previous backup if needed
```

#### 3. Rollback Deployment
```bash
# Keep previous version for quick rollback
cd /home/gladschool
git tag production-$(date +%Y%m%d-%H%M%S)
# To rollback: git checkout previous-tag
# sudo systemctl restart glad-school
```

### Monitoring Commands
```bash
# System health
df -h  # Disk usage
free -h  # Memory usage
top  # CPU usage
netstat -tulpn  # Network connections

# Application health
sudo systemctl status glad-school nginx postgresql redis-server
curl -I https://yourdomain.com  # Check site response

# Logs
tail -f /var/log/nginx/error.log
tail -f /home/gladschool/glad_tidings_school_mgmt/logs/production.log
sudo journalctl -u glad-school -f
```

This guide provides comprehensive instructions for deploying and maintaining the Glad Tidings School Management System in production. Follow these procedures for a secure, performant, and reliable deployment.
