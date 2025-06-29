#!/bin/bash

# Glad Tidings School Management System - Production Deployment Script
# This script automates the deployment process for production environments

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="glad_school_portal"
PROJECT_DIR="/var/www/glad_school"
BACKUP_DIR="/var/backups/glad_school"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="/var/log/glad_school_deploy.log"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to log actions
log_action() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if running as root
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root for security reasons"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3.9 &> /dev/null && ! command -v python3.10 &> /dev/null && ! command -v python3.11 &> /dev/null; then
        print_error "Python 3.9+ is required"
        exit 1
    fi
    
    # Check PostgreSQL
    if ! command -v psql &> /dev/null; then
        print_warning "PostgreSQL client not found. Make sure PostgreSQL is installed."
    fi
    
    # Check Redis
    if ! command -v redis-cli &> /dev/null; then
        print_warning "Redis client not found. Make sure Redis is installed."
    fi
    
    # Check Nginx
    if ! command -v nginx &> /dev/null; then
        print_warning "Nginx not found. Web server configuration may be needed."
    fi
    
    print_success "System requirements check completed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p "$PROJECT_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "/var/log"
    mkdir -p "$PROJECT_DIR/staticfiles"
    mkdir -p "$PROJECT_DIR/media"
    mkdir -p "$PROJECT_DIR/logs"
    
    print_success "Directories created"
}

# Setup Python virtual environment
setup_virtualenv() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip wheel setuptools
    
    print_success "Virtual environment setup completed"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    source "$VENV_DIR/bin/activate"
    pip install -r requirements.txt --no-cache-dir
    
    print_success "Dependencies installed"
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    source "$VENV_DIR/bin/activate"
    
    # Run migrations
    python manage.py migrate --settings=glad_school_portal.settings_production
    
    # Collect static files
    python manage.py collectstatic --noinput --settings=glad_school_portal.settings_production
    
    print_success "Database setup completed"
}

# Create superuser if it doesn't exist
create_superuser() {
    print_status "Creating superuser if needed..."
    
    source "$VENV_DIR/bin/activate"
    
    python manage.py shell --settings=glad_school_portal.settings_production << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@gladtidingsschool.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
EOF
    
    print_success "Superuser check completed"
}

# Setup systemd service
setup_systemd_service() {
    print_status "Setting up systemd service..."
    
    cat > "/tmp/glad-school.service" << EOF
[Unit]
Description=Glad Tidings School Management System
After=network.target

[Service]
Type=notify
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$VENV_DIR/bin
Environment=DJANGO_SETTINGS_MODULE=glad_school_portal.settings_production
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind unix:$PROJECT_DIR/glad_school.sock glad_school_portal.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    print_status "Systemd service file created. Please copy it to /etc/systemd/system/ as root:"
    echo "sudo cp /tmp/glad-school.service /etc/systemd/system/"
    echo "sudo systemctl daemon-reload"
    echo "sudo systemctl enable glad-school"
    echo "sudo systemctl start glad-school"
}

# Setup Nginx configuration
setup_nginx() {
    print_status "Setting up Nginx configuration..."
    
    cat > "/tmp/glad-school-nginx.conf" << EOF
upstream glad_school_app {
    server unix:$PROJECT_DIR/glad_school.sock;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    client_max_body_size 5M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root $PROJECT_DIR;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root $PROJECT_DIR;
        expires 1y;
        add_header Cache-Control "public";
    }

    location / {
        include proxy_params;
        proxy_pass http://glad_school_app;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Host \$http_host;
        proxy_redirect off;
    }
}
EOF
    
    print_status "Nginx configuration created. Please copy it to /etc/nginx/sites-available/ as root:"
    echo "sudo cp /tmp/glad-school-nginx.conf /etc/nginx/sites-available/glad-school"
    echo "sudo ln -s /etc/nginx/sites-available/glad-school /etc/nginx/sites-enabled/"
    echo "sudo nginx -t"
    echo "sudo systemctl restart nginx"
}

# Run security checks
run_security_checks() {
    print_status "Running security checks..."
    
    source "$VENV_DIR/bin/activate"
    python manage.py check --deploy --settings=glad_school_portal.settings_production
    
    print_success "Security checks completed"
}

# Create deployment backup
create_backup() {
    print_status "Creating deployment backup..."
    
    BACKUP_FILE="$BACKUP_DIR/deployment_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    tar -czf "$BACKUP_FILE" \
        --exclude="$VENV_DIR" \
        --exclude="*.pyc" \
        --exclude="__pycache__" \
        "$PROJECT_DIR"
    
    print_success "Backup created: $BACKUP_FILE"
}

# Main deployment function
deploy() {
    print_status "Starting deployment of Glad Tidings School Management System..."
    log_action "Deployment started"
    
    check_permissions
    check_requirements
    create_directories
    setup_virtualenv
    install_dependencies
    setup_database
    create_superuser
    run_security_checks
    create_backup
    setup_systemd_service
    setup_nginx
    
    print_success "Deployment completed successfully!"
    print_status "Next steps:"
    echo "1. Copy and configure the systemd service file"
    echo "2. Copy and configure the Nginx configuration"
    echo "3. Obtain and configure SSL certificates"
    echo "4. Update the .env.production file with your settings"
    echo "5. Test the deployment"
    
    log_action "Deployment completed successfully"
}

# Help function
show_help() {
    echo "Glad Tidings School Management System - Deployment Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  deploy     Run full deployment process"
    echo "  backup     Create backup only"
    echo "  check      Run security checks only"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy    # Full deployment"
    echo "  $0 backup    # Create backup"
    echo "  $0 check     # Security checks"
}

# Parse command line arguments
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    backup)
        create_backup
        ;;
    check)
        run_security_checks
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
