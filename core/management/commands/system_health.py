import os
from typing import Optional
from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps


class Command(BaseCommand):
    help = 'Generate comprehensive system health report'

    def handle(self, *args, **options) -> None:
        """Generate system health report"""
        
        self.stdout.write(self.style.SUCCESS('=== GLAD TIDINGS SCHOOL SYSTEM HEALTH REPORT ===\n'))
        
        # Database health
        self.check_database_health()
        
        # Model statistics
        self.generate_model_statistics()
        
        # File system checks
        self.check_file_system()
        
        # Cache status
        self.check_cache_status()
        
        self.stdout.write(self.style.SUCCESS('\n=== REPORT COMPLETE ==='))

    def check_database_health(self) -> None:
        """Check database connectivity and basic stats"""
        self.stdout.write(self.style.HTTP_INFO('DATABASE HEALTH:'))
        
        try:
            from django.db import connection
            
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write('✓ Database connection: OK')
            
            # Check database engine
            engine = settings.DATABASES['default']['ENGINE']
            self.stdout.write(f'✓ Database engine: {engine}')
            
            # Get table count
            table_count = len(connection.introspection.table_names())
            self.stdout.write(f'✓ Total tables: {table_count}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database error: {str(e)}'))
        
        self.stdout.write('')

    def generate_model_statistics(self) -> None:
        """Generate statistics for all models"""
        self.stdout.write(self.style.HTTP_INFO('MODEL STATISTICS:'))
        
        try:
            # Get all models
            all_models = apps.get_models()
            
            for model in all_models:
                if hasattr(model, '_meta'):
                    app_label = model._meta.app_label
                    model_name = model._meta.model_name
                    
                    try:
                        count = model.objects.count()
                        self.stdout.write(f'✓ {app_label}.{model_name}: {count} records')
                    except Exception as e:
                        self.stdout.write(f'✗ {app_label}.{model_name}: Error - {str(e)}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Model statistics error: {str(e)}'))
        
        self.stdout.write('')

    def check_file_system(self) -> None:
        """Check file system health"""
        self.stdout.write(self.style.HTTP_INFO('FILE SYSTEM:'))
        
        # Check important directories
        directories = [
            ('BASE_DIR', settings.BASE_DIR),
            ('STATIC_ROOT', getattr(settings, 'STATIC_ROOT', None)),
            ('MEDIA_ROOT', getattr(settings, 'MEDIA_ROOT', None)),
        ]
        
        for name, path in directories:
            if path and os.path.exists(path):
                # Get directory size
                size = self.get_directory_size(path)
                self.stdout.write(f'✓ {name}: {path} ({size})')
            elif path:
                self.stdout.write(f'✗ {name}: {path} (not found)')
            else:
                self.stdout.write(f'! {name}: Not configured')
        
        # Check logs directory
        logs_dir = os.path.join(str(settings.BASE_DIR), 'logs')
        if os.path.exists(logs_dir):
            log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
            self.stdout.write(f'✓ Logs directory: {len(log_files)} log files')
        else:
            self.stdout.write('! Logs directory: Not found')
        
        self.stdout.write('')

    def check_cache_status(self) -> None:
        """Check cache configuration and status"""
        self.stdout.write(self.style.HTTP_INFO('CACHE STATUS:'))
        
        try:
            from django.core.cache import cache
            
            # Test cache
            test_key = 'health_check_test'
            test_value = 'test_value'
            
            cache.set(test_key, test_value, 60)
            retrieved_value = cache.get(test_key)
            
            if retrieved_value == test_value:
                self.stdout.write('✓ Cache: Working')
                cache.delete(test_key)
            else:
                self.stdout.write('✗ Cache: Not working properly')
            
            # Cache backend info
            cache_backend = settings.CACHES['default']['BACKEND']
            self.stdout.write(f'✓ Cache backend: {cache_backend}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Cache error: {str(e)}'))
        
        self.stdout.write('')

    def get_directory_size(self, path: str) -> str:
        """Get human-readable directory size"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except (OSError, PermissionError):
            return "Unknown"
        
        # Convert to human readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024.0:
                return f"{total_size:.1f} {unit}"
            total_size /= 1024.0
        return f"{total_size:.1f} TB"
