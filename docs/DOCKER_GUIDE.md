# 🐳 Docker Deployment Guide

This document explains how to deploy the Glad Tidings School Management System using Docker.

## 📋 Prerequisites

- **Docker** installed on your system
- **Docker Compose** installed
- **Git** (to clone the repository)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/idorenyinbassey/glad_tidings_school_mgmt.git
cd glad_tidings_school_mgmt
```

### 2. Choose Your Deployment Method

#### Option A: Interactive Script (Recommended)
```bash
# Make the script executable
chmod +x docker_deploy.sh

# Run the deployment script
./docker_deploy.sh
```

#### Option B: Manual Commands

**Development Mode (SQLite):**
```bash
docker-compose -f docker-compose.dev.yml up --build -d
```

**Production Mode (PostgreSQL + Redis + Nginx):**
```bash
# Copy environment file and edit it
cp .env.docker .env
# Edit .env with your production values

# Start services
docker-compose up --build -d
```

## 🔧 Environment Configuration

### Development (.env not needed)
Development mode uses default settings and SQLite.

### Production (.env required)
Copy `.env.docker` to `.env` and configure:

```bash
# Database
DB_NAME=glad_school_db
DB_USER=glad_user  
DB_PASSWORD=your_secure_password

# Django
SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,localhost

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

## 🌐 Access Your Application

### Development Mode
- **Application**: http://localhost:8000
- **Admin**: http://localhost:8000/admin

### Production Mode  
- **Application**: http://localhost
- **Admin**: http://localhost/admin

## 📊 Service Overview

### Development Stack
- **Web**: Django application (port 8000)
- **Database**: SQLite (file-based)

### Production Stack
- **Web**: Django application
- **Database**: PostgreSQL (port 5432)
- **Cache**: Redis (port 6379)
- **Proxy**: Nginx (ports 80/443)

## 🛠️ Management Commands

### View Running Services
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx
```

### Access Container Shell
```bash
# Django application container
docker-compose exec web bash

# Database container
docker-compose exec db psql -U glad_user -d glad_school_db
```

### Django Management Commands
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic

# Run custom management commands
docker-compose exec web python manage.py system_health
docker-compose exec web python manage.py backup_db
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 🔄 Updates and Maintenance

### Update Application Code
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose up --build -d
```

### Database Backup
```bash
# Manual backup
docker-compose exec web python manage.py backup_db

# Or backup PostgreSQL directly
docker-compose exec db pg_dump -U glad_user glad_school_db > backup.sql
```

### Health Monitoring
```bash
# System health check
docker-compose exec web python manage.py system_health

# Performance report
docker-compose exec web python manage.py performance_report

# Security audit
docker-compose exec web python manage.py security_audit
```

## 🔒 Security Considerations

### Production Checklist
- ✅ Set strong `SECRET_KEY`
- ✅ Configure `ALLOWED_HOSTS` properly
- ✅ Use strong database passwords
- ✅ Enable HTTPS (configure SSL certificates)
- ✅ Set up proper firewall rules
- ✅ Regular security updates
- ✅ Monitor logs for suspicious activity

### SSL/HTTPS Setup
For production HTTPS, modify `docker/nginx/default.conf`:
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ... rest of configuration
}
```

## 🚨 Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8000

# Stop the process or change port in docker-compose.yml
```

**Permission Denied:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x docker_deploy.sh
```

**Database Connection Errors:**
```bash
# Check database service health
docker-compose logs db

# Restart database service
docker-compose restart db
```

**Memory Issues:**
```bash
# Increase Docker memory limits
# Or reduce worker processes in nginx.conf
```

### Logs Location
- **Application logs**: `logs/` directory
- **Container logs**: `docker-compose logs`
- **Nginx logs**: Inside nginx container at `/var/log/nginx/`

## 📈 Scaling and Performance

### Horizontal Scaling
```yaml
# In docker-compose.yml
services:
  web:
    deploy:
      replicas: 3
```

### Performance Optimization
- Use Redis for session storage
- Configure proper database indexes
- Set up CDN for static files
- Monitor with application performance monitoring (APM)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test with Docker: `docker-compose -f docker-compose.dev.yml up`
4. Submit a pull request

## 📞 Support

For issues related to Docker deployment:
1. Check this documentation
2. Review Docker logs: `docker-compose logs`
3. Check GitHub Issues
4. Contact: idorenyinbassey@gmail.com

---

**Happy Deploying! 🚀**
