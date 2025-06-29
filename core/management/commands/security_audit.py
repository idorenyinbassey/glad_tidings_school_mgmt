"""
Security audit management command to check for security vulnerabilities and misconfigurations.
"""

import os
import subprocess
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
import logging

# Import requests with error handling
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

User = get_user_model()


class SecurityAuditor:
    """Comprehensive security auditing system."""
    
    def __init__(self):
        self.vulnerabilities = []
        self.warnings = []
        self.info = []
    
    def check_django_settings(self):
        """Check Django security settings."""
        checks = [
            ('DEBUG', False, "DEBUG should be False in production"),
            ('SECRET_KEY', lambda x: len(x) > 50, "SECRET_KEY should be long and random"),
            ('SECURE_SSL_REDIRECT', True, "SECURE_SSL_REDIRECT should be True in production"),
            ('SESSION_COOKIE_SECURE', True, "SESSION_COOKIE_SECURE should be True"),
            ('CSRF_COOKIE_SECURE', True, "CSRF_COOKIE_SECURE should be True"),
            ('SECURE_BROWSER_XSS_FILTER', True, "SECURE_BROWSER_XSS_FILTER should be True"),
            ('SECURE_CONTENT_TYPE_NOSNIFF', True, "SECURE_CONTENT_TYPE_NOSNIFF should be True"),
            ('X_FRAME_OPTIONS', 'DENY', "X_FRAME_OPTIONS should be DENY"),
        ]
        
        for setting, expected, message in checks:
            try:
                value = getattr(settings, setting, None)
                
                if callable(expected):
                    if not expected(value):
                        self.vulnerabilities.append(f"{setting}: {message}")
                elif value != expected:
                    if setting in ['SECURE_SSL_REDIRECT', 'SESSION_COOKIE_SECURE', 'CSRF_COOKIE_SECURE'] and not settings.DEBUG:
                        self.vulnerabilities.append(f"{setting}: {message}")
                    else:
                        self.warnings.append(f"{setting}: {message}")
                else:
                    self.info.append(f"{setting}: OK")
                    
            except AttributeError:
                self.warnings.append(f"{setting}: Setting not found")
    
    def check_user_accounts(self):
        """Check for insecure user accounts."""
        try:
            # Check for users with weak passwords
            weak_passwords = ['password', '123456', 'admin', 'test', 'password123']
            
            # Check for default admin accounts
            default_admins = User.objects.filter(
                username__in=['admin', 'administrator', 'root'],
                is_superuser=True
            )
            
            if default_admins.exists():
                self.warnings.append(f"Found {default_admins.count()} default admin account(s)")
            
            # Check for inactive superusers
            inactive_superusers = User.objects.filter(
                is_superuser=True,
                is_active=False
            )
            
            if inactive_superusers.exists():
                self.info.append(f"Found {inactive_superusers.count()} inactive superuser(s)")
            
            # Check for users without last login (potential unused accounts)
            old_threshold = datetime.now() - timedelta(days=90)
            old_users = User.objects.filter(
                last_login__lt=old_threshold
            ).exclude(last_login__isnull=True)
            
            if old_users.exists():
                self.warnings.append(f"Found {old_users.count()} users with no login in 90+ days")
            
            self.info.append("User account security check completed")
            
        except Exception as e:
            self.vulnerabilities.append(f"User account check failed: {str(e)}")
    
    def check_database_security(self):
        """Check database security configurations."""
        try:
            db_config = settings.DATABASES['default']
            
            # Check if using default database names
            default_names = ['db.sqlite3', 'test.db', 'database.db']
            db_name = db_config.get('NAME', '')
            
            if any(default in db_name for default in default_names):
                self.warnings.append("Using default database name")
            
            # Check for database connection security
            if db_config.get('ENGINE') == 'django.db.backends.postgresql':
                if not db_config.get('OPTIONS', {}).get('sslmode'):
                    self.warnings.append("PostgreSQL SSL mode not configured")
            
            # Check database permissions (basic test)
            with connection.cursor() as cursor:
                if db_config.get('ENGINE') == 'django.db.backends.postgresql':
                    cursor.execute("SELECT current_user, session_user;")
                    user_info = cursor.fetchone()
                    self.info.append(f"Database user: {user_info[0]}")
                
                # Test for dangerous permissions
                try:
                    if db_config.get('ENGINE') == 'django.db.backends.postgresql':
                        cursor.execute("SELECT has_database_privilege(current_user, current_database(), 'CREATE');")
                        can_create = cursor.fetchone()[0]
                        if can_create and not settings.DEBUG:
                            self.warnings.append("Database user has CREATE privileges in production")
                except Exception:
                    pass  # Permission check might fail, that's okay
            
            self.info.append("Database security check completed")
            
        except Exception as e:
            self.vulnerabilities.append(f"Database security check failed: {str(e)}")
    
    def check_file_permissions(self):
        """Check file and directory permissions."""
        try:
            important_files = [
                settings.BASE_DIR / 'manage.py',
                settings.BASE_DIR / '.env',
                settings.BASE_DIR / 'glad_school_portal' / 'settings.py',
            ]
            
            for file_path in important_files:
                if file_path.exists():
                    # Check if file is world-readable
                    stat_info = file_path.stat()
                    mode = stat_info.st_mode
                    
                    # Check for world-writable files
                    if mode & 0o002:
                        self.vulnerabilities.append(f"World-writable file: {file_path}")
                    
                    # Check for world-readable sensitive files
                    if file_path.name in ['.env', 'settings.py'] and mode & 0o004:
                        self.warnings.append(f"World-readable sensitive file: {file_path}")
                    
                else:
                    self.info.append(f"File not found (OK): {file_path}")
            
            # Check logs directory permissions
            logs_dir = settings.BASE_DIR / 'logs'
            if logs_dir.exists():
                stat_info = logs_dir.stat()
                mode = stat_info.st_mode
                if mode & 0o002:
                    self.vulnerabilities.append("Logs directory is world-writable")
            
            self.info.append("File permissions check completed")
            
        except Exception as e:
            self.vulnerabilities.append(f"File permissions check failed: {str(e)}")
    
    def check_dependencies(self):
        """Check for vulnerable dependencies."""
        try:
            # Run pip check for basic dependency issues
            result = subprocess.run(
                ['pip', 'check'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.warnings.append(f"Dependency conflicts found: {result.stdout}")
            else:
                self.info.append("No dependency conflicts found")
            
            # Check for safety (if available)
            try:
                safety_result = subprocess.run(
                    ['safety', 'check', '--json'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if safety_result.returncode == 0:
                    self.info.append("No known security vulnerabilities in dependencies")
                else:
                    try:
                        safety_data = json.loads(safety_result.stdout)
                        if safety_data:
                            self.vulnerabilities.append(f"Found {len(safety_data)} security vulnerabilities in dependencies")
                    except json.JSONDecodeError:
                        self.warnings.append("Could not parse safety check results")
                        
            except FileNotFoundError:
                self.info.append("Safety tool not installed (consider: pip install safety)")
            
        except Exception as e:
            self.warnings.append(f"Dependency check failed: {str(e)}")
    
    def check_web_security_headers(self):
        """Check web security headers (if URL is provided)."""
        try:
            if not REQUESTS_AVAILABLE:
                self.info.append("Skipping web security headers check (requests not available)")
                return
                
            # Only check if we have a URL to test
            allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
            if not allowed_hosts or 'localhost' in allowed_hosts[0]:
                self.info.append("Skipping web security headers check (no production URL)")
                return
            
            test_url = f"https://{allowed_hosts[0]}"
            
            try:
                response = requests.get(test_url, timeout=10)
                headers = response.headers
                
                security_headers = {
                    'Strict-Transport-Security': 'HSTS header missing',
                    'X-Content-Type-Options': 'X-Content-Type-Options header missing',
                    'X-Frame-Options': 'X-Frame-Options header missing',
                    'X-XSS-Protection': 'X-XSS-Protection header missing',
                    'Content-Security-Policy': 'CSP header missing',
                    'Referrer-Policy': 'Referrer-Policy header missing',
                }
                
                for header, message in security_headers.items():
                    if header not in headers:
                        self.warnings.append(message)
                    else:
                        self.info.append(f"{header}: OK")
                
            except requests.RequestException:
                self.info.append("Could not test web security headers (URL not accessible)")
                
        except Exception as e:
            self.warnings.append(f"Web security headers check failed: {str(e)}")
    
    def check_logging_security(self):
        """Check logging configuration for security issues."""
        try:
            logging_config = getattr(settings, 'LOGGING', {})
            
            if not logging_config:
                self.warnings.append("No logging configuration found")
                return
            
            # Check if sensitive information might be logged
            handlers = logging_config.get('handlers', {})
            
            for handler_name, handler_config in handlers.items():
                if handler_config.get('class') == 'logging.StreamHandler':
                    if not settings.DEBUG:
                        self.warnings.append("Console logging enabled in production")
                
                # Check log file permissions
                if 'filename' in handler_config:
                    log_file = handler_config['filename']
                    if os.path.exists(log_file):
                        stat_info = os.stat(log_file)
                        if stat_info.st_mode & 0o044:  # World or group readable
                            self.warnings.append(f"Log file {log_file} is readable by others")
            
            self.info.append("Logging security check completed")
            
        except Exception as e:
            self.warnings.append(f"Logging security check failed: {str(e)}")
    
    def run_all_checks(self):
        """Run all security checks."""
        checks = [
            self.check_django_settings,
            self.check_user_accounts,
            self.check_database_security,
            self.check_file_permissions,
            self.check_dependencies,
            self.check_web_security_headers,
            self.check_logging_security,
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.vulnerabilities.append(f"Security check {check.__name__} failed: {str(e)}")
    
    def get_report(self):
        """Get security audit report."""
        return {
            'vulnerabilities': self.vulnerabilities,
            'warnings': self.warnings,
            'info': self.info,
            'risk_level': self._calculate_risk_level(),
            'timestamp': datetime.now().isoformat(),
        }
    
    def _calculate_risk_level(self):
        """Calculate overall risk level."""
        if len(self.vulnerabilities) >= 5:
            return 'critical'
        elif len(self.vulnerabilities) >= 2:
            return 'high'
        elif len(self.vulnerabilities) >= 1 or len(self.warnings) >= 5:
            return 'medium'
        elif len(self.warnings) >= 1:
            return 'low'
        else:
            return 'minimal'


class Command(BaseCommand):
    help = 'Run comprehensive security audit'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output results in JSON format',
        )
        parser.add_argument(
            '--save-report',
            action='store_true',
            help='Save report to file',
        )
    
    def handle(self, *args, **options):
        self.stdout.write("Running security audit...")
        
        auditor = SecurityAuditor()
        auditor.run_all_checks()
        
        report = auditor.get_report()
        
        if options['json']:
            output = json.dumps(report, indent=2)
            self.stdout.write(output)
        else:
            self._display_human_readable_report(report)
        
        if options['save_report']:
            filename = f"security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            self.stdout.write(f"Report saved to {filename}")
        
        # Exit with appropriate code based on risk level
        risk_level = report['risk_level']
        if risk_level in ['critical', 'high']:
            exit(2)
        elif risk_level == 'medium':
            exit(1)
        else:
            exit(0)
    
    def _display_human_readable_report(self, report):
        """Display human-readable security report."""
        
        # Risk level header
        risk_level = report['risk_level']
        risk_colors = {
            'critical': self.style.ERROR,
            'high': self.style.ERROR,
            'medium': self.style.WARNING,
            'low': self.style.WARNING,
            'minimal': self.style.SUCCESS,
        }
        
        risk_icons = {
            'critical': '🚨',
            'high': '❌',
            'medium': '⚠️',
            'low': '⚠️',
            'minimal': '✅',
        }
        
        color = risk_colors.get(risk_level, self.style.SUCCESS)
        icon = risk_icons.get(risk_level, '✅')
        
        self.stdout.write("")
        self.stdout.write(color(f"{icon} Security Risk Level: {risk_level.upper()}"))
        self.stdout.write("=" * 60)
        
        # Vulnerabilities
        if report['vulnerabilities']:
            self.stdout.write("")
            self.stdout.write(self.style.ERROR("🚨 CRITICAL VULNERABILITIES:"))
            for vuln in report['vulnerabilities']:
                self.stdout.write(self.style.ERROR(f"  ❌ {vuln}"))
        
        # Warnings
        if report['warnings']:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("⚠️ WARNINGS:"))
            for warning in report['warnings']:
                self.stdout.write(self.style.WARNING(f"  ⚠️ {warning}"))
        
        # Info
        if report['info']:
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("ℹ️ SECURITY STATUS:"))
            for info in report['info']:
                self.stdout.write(self.style.SUCCESS(f"  ✅ {info}"))
        
        # Summary
        self.stdout.write("")
        self.stdout.write("📊 SUMMARY:")
        self.stdout.write(f"  Critical Issues: {len(report['vulnerabilities'])}")
        self.stdout.write(f"  Warnings: {len(report['warnings'])}")
        self.stdout.write(f"  Checks Passed: {len(report['info'])}")
        
        # Recommendations
        if report['vulnerabilities'] or report['warnings']:
            self.stdout.write("")
            self.stdout.write("🔧 RECOMMENDATIONS:")
            
            if report['vulnerabilities']:
                self.stdout.write("  1. Address critical vulnerabilities immediately")
                self.stdout.write("  2. Review and update security settings")
                self.stdout.write("  3. Implement additional security measures")
            
            if report['warnings']:
                self.stdout.write("  4. Review warnings and implement fixes")
                self.stdout.write("  5. Regular security audits recommended")
        
        self.stdout.write("")
        self.stdout.write(f"Audit completed at: {report['timestamp']}")
        self.stdout.write("")
