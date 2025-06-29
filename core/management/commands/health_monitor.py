"""
Advanced health monitoring and alerting system for production.
"""

import os
import json
import smtplib
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.core.mail import send_mail
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Import optional dependencies with error handling
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Comprehensive health monitoring system."""
    
    def __init__(self):
        self.alerts = []
        self.warnings = []
        self.info = []
        
    def check_database_health(self):
        """Check database connectivity and performance."""
        try:
            with connection.cursor() as cursor:
                # Test basic connectivity
                cursor.execute("SELECT 1")
                
                # Check connection pool if using PostgreSQL
                if hasattr(connection, 'vendor') and connection.vendor == 'postgresql':
                    cursor.execute("""
                        SELECT count(*) as active_connections 
                        FROM pg_stat_activity 
                        WHERE state = 'active'
                    """)
                    active_connections = cursor.fetchone()[0]
                    
                    if active_connections > 80:  # Alert if more than 80 connections
                        self.alerts.append(f"High database connections: {active_connections}")
                    elif active_connections > 50:
                        self.warnings.append(f"Moderate database connections: {active_connections}")
                    
                    # Check slow queries
                    cursor.execute("""
                        SELECT query, query_start, state 
                        FROM pg_stat_activity 
                        WHERE state = 'active' 
                        AND query_start < now() - interval '30 seconds'
                        AND query NOT LIKE '%pg_stat_activity%'
                    """)
                    slow_queries = cursor.fetchall()
                    
                    if slow_queries:
                        self.warnings.append(f"Found {len(slow_queries)} slow running queries")
                
                self.info.append("Database connectivity: OK")
                return True
                
        except Exception as e:
            self.alerts.append(f"Database error: {str(e)}")
            return False
    
    def check_redis_health(self):
        """Check Redis connectivity and memory usage."""
        try:
            if not REDIS_AVAILABLE:
                self.info.append("Redis check skipped (redis not available)")
                return True
                
            r = redis.Redis.from_url(settings.CACHES['default']['LOCATION'])
            
            # Test connectivity
            r.ping()
            
            # Check memory usage
            info = r.info('memory')
            used_memory = info['used_memory']
            used_memory_mb = used_memory / (1024 * 1024)
            
            if used_memory_mb > 500:  # Alert if Redis uses more than 500MB
                self.alerts.append(f"High Redis memory usage: {used_memory_mb:.2f} MB")
            elif used_memory_mb > 250:
                self.warnings.append(f"Moderate Redis memory usage: {used_memory_mb:.2f} MB")
            
            # Check connected clients
            connected_clients = info.get('connected_clients', 0)
            if connected_clients > 100:
                self.warnings.append(f"High Redis client connections: {connected_clients}")
            
            self.info.append(f"Redis connectivity: OK (Memory: {used_memory_mb:.2f} MB)")
            return True
            
        except Exception as e:
            self.alerts.append(f"Redis error: {str(e)}")
            return False
    
    def check_disk_space(self):
        """Check disk space usage."""
        try:
            if not PSUTIL_AVAILABLE:
                self.info.append("Disk space check skipped (psutil not available)")
                return True
                
            disk_usage = psutil.disk_usage('/')
            percent_used = (disk_usage.used / disk_usage.total) * 100
            
            if percent_used > 90:
                self.alerts.append(f"Critical disk space: {percent_used:.1f}% used")
            elif percent_used > 80:
                self.warnings.append(f"High disk space usage: {percent_used:.1f}% used")
            
            self.info.append(f"Disk space: {percent_used:.1f}% used")
            return True
            
        except Exception as e:
            self.alerts.append(f"Disk check error: {str(e)}")
            return False
    
    def check_memory_usage(self):
        """Check system memory usage."""
        try:
            if not PSUTIL_AVAILABLE:
                self.info.append("Memory usage check skipped (psutil not available)")
                return True
                
            memory = psutil.virtual_memory()
            percent_used = memory.percent
            
            if percent_used > 90:
                self.alerts.append(f"Critical memory usage: {percent_used:.1f}%")
            elif percent_used > 80:
                self.warnings.append(f"High memory usage: {percent_used:.1f}%")
            
            self.info.append(f"Memory usage: {percent_used:.1f}%")
            return True
            
        except Exception as e:
            self.alerts.append(f"Memory check error: {str(e)}")
            return False
    
    def check_cpu_usage(self):
        """Check CPU usage."""
        try:
            if not PSUTIL_AVAILABLE:
                self.info.append("CPU usage check skipped (psutil not available)")
                return True
                
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent > 90:
                self.alerts.append(f"Critical CPU usage: {cpu_percent:.1f}%")
            elif cpu_percent > 80:
                self.warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            self.info.append(f"CPU usage: {cpu_percent:.1f}%")
            return True
            
        except Exception as e:
            self.alerts.append(f"CPU check error: {str(e)}")
            return False
    
    def check_application_health(self):
        """Check application-specific health metrics."""
        try:
            # Check if cache is working
            cache.set('health_check', 'ok', 60)
            if cache.get('health_check') != 'ok':
                self.alerts.append("Cache not working properly")
                return False
            
            # Check log file sizes
            log_dir = getattr(settings, 'BASE_DIR', '/tmp') / 'logs'
            if log_dir.exists():
                for log_file in log_dir.glob('*.log'):
                    size_mb = log_file.stat().st_size / (1024 * 1024)
                    if size_mb > 100:  # Alert if log file is larger than 100MB
                        self.warnings.append(f"Large log file: {log_file.name} ({size_mb:.1f} MB)")
            
            self.info.append("Application health: OK")
            return True
            
        except Exception as e:
            self.alerts.append(f"Application health check error: {str(e)}")
            return False
    
    def check_ssl_certificate(self, domain=None):
        """Check SSL certificate expiration."""
        if not domain:
            return True
            
        try:
            import ssl
            import socket
            from datetime import datetime
            
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
            # Check expiration
            expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_until_expiry = (expiry_date - datetime.now()).days
            
            if days_until_expiry < 7:
                self.alerts.append(f"SSL certificate expires in {days_until_expiry} days")
            elif days_until_expiry < 30:
                self.warnings.append(f"SSL certificate expires in {days_until_expiry} days")
            
            self.info.append(f"SSL certificate: {days_until_expiry} days until expiry")
            return True
            
        except Exception as e:
            self.warnings.append(f"SSL check error: {str(e)}")
            return False
    
    def send_alerts(self):
        """Send alerts via email if there are any."""
        if not (self.alerts or self.warnings):
            return
        
        try:
            subject = "Glad School System Health Alert"
            
            message_parts = []
            
            if self.alerts:
                message_parts.append("🚨 CRITICAL ALERTS:")
                message_parts.extend([f"  - {alert}" for alert in self.alerts])
                message_parts.append("")
            
            if self.warnings:
                message_parts.append("⚠️ WARNINGS:")
                message_parts.extend([f"  - {warning}" for warning in self.warnings])
                message_parts.append("")
            
            if self.info:
                message_parts.append("ℹ️ SYSTEM STATUS:")
                message_parts.extend([f"  - {info}" for info in self.info])
            
            message_parts.append(f"\nChecked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            message = "\n".join(message_parts)
            
            # Send email to admins
            if hasattr(settings, 'ADMINS') and settings.ADMINS:
                admin_emails = [admin[1] for admin in settings.ADMINS]
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    admin_emails,
                    fail_silently=False,
                )
                logger.info(f"Health alert sent to {len(admin_emails)} administrators")
        
        except Exception as e:
            logger.error(f"Failed to send health alert: {str(e)}")
    
    def run_all_checks(self, domain=None):
        """Run all health checks."""
        checks = [
            self.check_database_health,
            self.check_redis_health,
            self.check_disk_space,
            self.check_memory_usage,
            self.check_cpu_usage,
            self.check_application_health,
        ]
        
        if domain:
            checks.append(lambda: self.check_ssl_certificate(domain))
        
        results = {}
        for check in checks:
            try:
                results[check.__name__] = check()
            except Exception as e:
                results[check.__name__] = False
                self.alerts.append(f"Check {check.__name__} failed: {str(e)}")
        
        return results
    
    def get_summary(self):
        """Get a summary of all checks."""
        return {
            'alerts': self.alerts,
            'warnings': self.warnings,
            'info': self.info,
            'status': 'critical' if self.alerts else 'warning' if self.warnings else 'ok',
            'timestamp': datetime.now().isoformat(),
        }


class Command(BaseCommand):
    help = 'Run comprehensive health monitoring checks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            help='Domain to check SSL certificate for',
        )
        parser.add_argument(
            '--send-alerts',
            action='store_true',
            help='Send email alerts if issues are found',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output results in JSON format',
        )
    
    def handle(self, *args, **options):
        monitor = HealthMonitor()
        
        self.stdout.write("Running health monitoring checks...")
        
        # Run all checks
        results = monitor.run_all_checks(domain=options.get('domain'))
        
        # Get summary
        summary = monitor.get_summary()
        
        if options['json']:
            # Output JSON for programmatic consumption
            output = {
                'results': results,
                'summary': summary,
            }
            self.stdout.write(json.dumps(output, indent=2))
        else:
            # Human-readable output
            if summary['alerts']:
                self.stdout.write(
                    self.style.ERROR(f"🚨 {len(summary['alerts'])} Critical Alert(s):")
                )
                for alert in summary['alerts']:
                    self.stdout.write(self.style.ERROR(f"  - {alert}"))
                self.stdout.write("")
            
            if summary['warnings']:
                self.stdout.write(
                    self.style.WARNING(f"⚠️ {len(summary['warnings'])} Warning(s):")
                )
                for warning in summary['warnings']:
                    self.stdout.write(self.style.WARNING(f"  - {warning}"))
                self.stdout.write("")
            
            if summary['info']:
                self.stdout.write(
                    self.style.SUCCESS(f"ℹ️ System Status:")
                )
                for info in summary['info']:
                    self.stdout.write(self.style.SUCCESS(f"  - {info}"))
            
            # Overall status
            status_color = {
                'critical': self.style.ERROR,
                'warning': self.style.WARNING,
                'ok': self.style.SUCCESS,
            }[summary['status']]
            
            self.stdout.write("")
            self.stdout.write(
                status_color(f"Overall Status: {summary['status'].upper()}")
            )
        
        # Send alerts if requested
        if options['send_alerts']:
            monitor.send_alerts()
        
        # Exit with appropriate code
        if summary['status'] == 'critical':
            exit(2)
        elif summary['status'] == 'warning':
            exit(1)
        else:
            exit(0)
