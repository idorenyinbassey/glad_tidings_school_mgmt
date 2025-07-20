#!/bin/bash

# LAMP Stack Deployment Script for Glad Tidings School Management Portal
# This script automates the deployment process on a LAMP server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="glad_school"
PROJECT_DIR="/var/www/$PROJECT_NAME"
VENV_DIR="$PROJECT_DIR/venv"
DB_NAME="glad_school_db"
DB_USER="glad_user"
APACHE_SITE_CONF="/etc/apache2/sites-available/$PROJECT_NAME.conf"

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

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
        exit 1
    fi
}

# Function to install system dependencies
install_system_dependencies() {
    print_status "Installing system dependencies..."
    
    # Detect OS
    if [[ -f /etc/debian_version ]]; then
        # Debian/Ubuntu
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv python3-dev
        sudo apt install -y apache2 mysql-server mysql-client libmysqlclient-dev
        sudo apt install -y libapache2-mod-wsgi-py3
        sudo apt install -y git curl wget
        
        # Enable Apache modules
        sudo a2enmod wsgi rewrite ssl headers expires
        
    elif [[ -f /etc/redhat-release ]]; then
        # CentOS/RHEL
        sudo yum update -y
        sudo yum install -y python3 python3-pip python3-devel
        sudo yum install -y httpd mysql-server mysql-devel
        sudo yum install -y python3-mod_wsgi
        sudo yum install -y git curl wget
        
        # Start services
        sudo systemctl enable httpd mysql
        sudo systemctl start httpd mysql
        
    else
        print_error "Unsupported operating system"
        exit 1
    fi
    
    print_success "System dependencies installed"
}

# Function to secure MySQL
secure_mysql() {
    print_status "Setting up MySQL database..."
    
    # Generate a random password
    DB_PASSWORD=$(openssl rand -base64 32)
    
    # Create database and user
    sudo mysql -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    sudo mysql -e "CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';"
    sudo mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';"
    sudo mysql -e "FLUSH PRIVILEGES;"
    
    # Save database credentials
    echo "# Database credentials for $PROJECT_NAME" > ~/.mysql_credentials
    echo "DB_NAME=$DB_NAME" >> ~/.mysql_credentials
    echo "DB_USER=$DB_USER" >> ~/.mysql_credentials
    echo "DB_PASSWORD=$DB_PASSWORD" >> ~/.mysql_credentials
    chmod 600 ~/.mysql_credentials
    
    print_success "MySQL database configured. Credentials saved to ~/.mysql_credentials"
}

# Function to create project directory structure
setup_project_directory() {
    print_status "Setting up project directory..."
    
    # Create project directory
    sudo mkdir -p $PROJECT_DIR
    sudo chown -R $USER:www-data $PROJECT_DIR
    sudo chmod -R 755 $PROJECT_DIR
    
    # Create subdirectories
    mkdir -p $PROJECT_DIR/{static,media,logs,backups}
    
    print_success "Project directory structure created"
}

# Function to setup Python virtual environment
setup_python_environment() {
    print_status "Setting up Python virtual environment..."
    
    cd $PROJECT_DIR
    python3 -m venv $VENV_DIR
    source $VENV_DIR/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install LAMP-specific requirements
    if [[ -f requirements_lamp.txt ]]; then
        pip install -r requirements_lamp.txt
    else
        print_warning "requirements_lamp.txt not found. Installing basic Django requirements..."
        pip install Django mysqlclient whitenoise gunicorn
    fi
    
    print_success "Python environment configured"
}

# Function to configure Django settings
configure_django() {
    print_status "Configuring Django settings..."
    
    source ~/.mysql_credentials
    
    # Create .env file
    cat > $PROJECT_DIR/.env << EOF
DEBUG=False
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=localhost,127.0.0.1,$(hostname -f)

# Database
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=3306

# Email settings (configure these)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# School settings
SCHOOL_NAME=Glad Tidings School
SCHOOL_ADDRESS=Your School Address
SCHOOL_PHONE=+234-xxx-xxx-xxxx
SCHOOL_EMAIL=info@gladtidingsschool.edu
EOF
    
    chmod 600 $PROJECT_DIR/.env
    
    print_success "Django configuration completed"
}

# Function to run Django migrations and setup
setup_django() {
    print_status "Setting up Django application..."
    
    cd $PROJECT_DIR
    source $VENV_DIR/bin/activate
    
    # Set Django settings module to LAMP configuration
    export DJANGO_SETTINGS_MODULE="glad_school_portal.settings_lamp"
    
    # Create cache table
    python manage.py createcachetable
    
    # Run migrations
    python manage.py migrate
    
    # Collect static files
    python manage.py collectstatic --noinput
    
    # Create superuser (interactive)
    print_status "Creating Django superuser..."
    python manage.py createsuperuser
    
    # Load initial data if available
    if [[ -f populate_classes_subjects.py ]]; then
        print_status "Populating classes and subjects..."
        python populate_classes_subjects.py
    fi
    
    if [[ -f create_test_users.py ]]; then
        print_status "Creating test users..."
        python create_test_users.py
    fi
    
    print_success "Django application setup completed"
}

# Function to configure Apache
configure_apache() {
    print_status "Configuring Apache web server..."
    
    # Create Apache configuration
    sudo tee $APACHE_SITE_CONF > /dev/null << EOF
<VirtualHost *:80>
    ServerName $(hostname -f)
    DocumentRoot $PROJECT_DIR
    
    # WSGI Configuration
    WSGIDaemonProcess $PROJECT_NAME python-home=$VENV_DIR python-path=$PROJECT_DIR
    WSGIProcessGroup $PROJECT_NAME
    WSGIScriptAlias / $PROJECT_DIR/glad_school_portal/wsgi.py
    WSGIApplicationGroup %{GLOBAL}
    
    # Django application directory
    <Directory $PROJECT_DIR/glad_school_portal>
        WSGIProcessGroup $PROJECT_NAME
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
    
    # Static files
    Alias /static $PROJECT_DIR/static
    <Directory $PROJECT_DIR/static>
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 1 year"
    </Directory>
    
    # Media files
    Alias /media $PROJECT_DIR/media
    <Directory $PROJECT_DIR/media>
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 1 month"
    </Directory>
    
    # Security headers
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
    
    # Logging
    ErrorLog \${APACHE_LOG_DIR}/${PROJECT_NAME}_error.log
    CustomLog \${APACHE_LOG_DIR}/${PROJECT_NAME}_access.log combined
    LogLevel info
</VirtualHost>
EOF
    
    # Enable site and disable default
    sudo a2ensite $PROJECT_NAME.conf
    sudo a2dissite 000-default.conf
    
    # Test Apache configuration
    sudo apache2ctl configtest
    
    if [[ $? -eq 0 ]]; then
        sudo systemctl reload apache2
        print_success "Apache configured successfully"
    else
        print_error "Apache configuration test failed"
        exit 1
    fi
}

# Function to set proper permissions
set_permissions() {
    print_status "Setting file permissions..."
    
    # Set ownership
    sudo chown -R www-data:www-data $PROJECT_DIR/media
    sudo chown -R www-data:www-data $PROJECT_DIR/static
    sudo chown -R www-data:www-data $PROJECT_DIR/logs
    
    # Set permissions
    find $PROJECT_DIR -type f -exec chmod 644 {} \;
    find $PROJECT_DIR -type d -exec chmod 755 {} \;
    
    # Make manage.py executable
    chmod +x $PROJECT_DIR/manage.py
    
    # Secure sensitive files
    chmod 600 $PROJECT_DIR/.env
    
    print_success "File permissions configured"
}

# Function to create backup script
create_backup_script() {
    print_status "Creating backup script..."
    
    source ~/.mysql_credentials
    
    cat > $PROJECT_DIR/backup.sh << 'EOF'
#!/bin/bash
# Backup script for Glad Tidings School Management Portal

BACKUP_DIR="/var/backups/glad_school"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="/var/www/glad_school"

# Create backup directory
mkdir -p $BACKUP_DIR

# Source database credentials
source ~/.mysql_credentials

# Database backup
echo "Backing up database..."
mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Media files backup
echo "Backing up media files..."
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz $PROJECT_DIR/media/

# Keep only last 7 days of backups
echo "Cleaning old backups..."
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF
    
    chmod +x $PROJECT_DIR/backup.sh
    
    # Add to crontab for daily backups
    (crontab -l 2>/dev/null; echo "0 2 * * * $PROJECT_DIR/backup.sh") | crontab -
    
    print_success "Backup script created and scheduled"
}

# Function to perform system tests
run_tests() {
    print_status "Running system tests..."
    
    cd $PROJECT_DIR
    source $VENV_DIR/bin/activate
    export DJANGO_SETTINGS_MODULE="glad_school_portal.settings_lamp"
    
    # Test Django
    python manage.py check
    
    # Test database connection
    python manage.py dbshell --command="SELECT 1;"
    
    # Test Apache
    curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "200\|302" || {
        print_error "Apache test failed"
        return 1
    }
    
    print_success "All tests passed"
}

# Function to display deployment summary
show_summary() {
    source ~/.mysql_credentials
    
    print_success "LAMP Deployment Complete!"
    echo ""
    echo "🎓 Glad Tidings School Management Portal"
    echo "=========================================="
    echo ""
    echo "📍 Installation Details:"
    echo "   Project Directory: $PROJECT_DIR"
    echo "   Virtual Environment: $VENV_DIR"
    echo "   Database: $DB_NAME"
    echo "   Database User: $DB_USER"
    echo ""
    echo "🌐 Access Information:"
    echo "   Web Interface: http://$(hostname -f)/"
    echo "   Admin Panel: http://$(hostname -f)/admin/"
    echo ""
    echo "📁 Important Files:"
    echo "   Environment Config: $PROJECT_DIR/.env"
    echo "   Apache Config: $APACHE_SITE_CONF"
    echo "   Database Credentials: ~/.mysql_credentials"
    echo "   Backup Script: $PROJECT_DIR/backup.sh"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Configure your domain name in Apache"
    echo "   2. Set up SSL certificate (Let's Encrypt recommended)"
    echo "   3. Configure email settings in .env"
    echo "   4. Test all functionality"
    echo "   5. Set up monitoring and alerts"
    echo ""
    echo "🔐 Security Notes:"
    echo "   - Database credentials are stored in ~/.mysql_credentials"
    echo "   - Change default passwords before production use"
    echo "   - Configure firewall rules as needed"
    echo "   - Regular backups are scheduled at 2 AM daily"
    echo ""
    print_success "Deployment completed successfully!"
}

# Main deployment function
main() {
    print_status "Starting LAMP deployment for Glad Tidings School Management Portal..."
    
    check_root
    
    echo "This script will:"
    echo "1. Install system dependencies (Apache, MySQL, Python)"
    echo "2. Configure MySQL database"
    echo "3. Set up Python virtual environment"
    echo "4. Configure Django application"
    echo "5. Set up Apache web server"
    echo "6. Configure permissions and security"
    echo "7. Create backup scripts"
    echo "8. Run system tests"
    echo ""
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Deployment cancelled"
        exit 0
    fi
    
    # Execute deployment steps
    install_system_dependencies
    secure_mysql
    setup_project_directory
    setup_python_environment
    configure_django
    setup_django
    configure_apache
    set_permissions
    create_backup_script
    
    # Run tests
    if run_tests; then
        show_summary
    else
        print_error "Deployment completed with some issues. Please check the logs."
        exit 1
    fi
}

# Run main function
main "$@"
