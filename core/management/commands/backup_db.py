import os
import subprocess
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection


class Command(BaseCommand):
    help = 'Backup database to a file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path for the backup',
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compress the backup file',
        )

    def handle(self, *args, **options):
        """Create a database backup"""
        
        # Get database configuration
        db_config = settings.DATABASES['default']
        engine = db_config['ENGINE']
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename if not provided
        if options['output']:
            backup_file = options['output']
        else:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')
        
        try:
            if 'sqlite3' in engine:
                self.backup_sqlite(db_config, backup_file)
            elif 'postgresql' in engine:
                self.backup_postgresql(db_config, backup_file)
            elif 'mysql' in engine:
                self.backup_mysql(db_config, backup_file)
            else:
                raise CommandError(f"Unsupported database engine: {engine}")
            
            # Compress if requested
            if options['compress']:
                self.compress_backup(backup_file)
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created backup: {backup_file}')
            )
            
        except Exception as e:
            raise CommandError(f'Backup failed: {str(e)}')

    def backup_sqlite(self, db_config, backup_file):
        """Backup SQLite database"""
        db_path = db_config['NAME']
        
        # Simple file copy for SQLite
        import shutil
        shutil.copy2(db_path, backup_file)
        
        self.stdout.write(f'SQLite database backed up to: {backup_file}')

    def backup_postgresql(self, db_config, backup_file):
        """Backup PostgreSQL database using pg_dump"""
        cmd = [
            'pg_dump',
            '-h', db_config.get('HOST', 'localhost'),
            '-p', str(db_config.get('PORT', 5432)),
            '-U', db_config['USER'],
            '-d', db_config['NAME'],
            '-f', backup_file,
            '--verbose'
        ]
        
        # Set password via environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise CommandError(f'pg_dump failed: {result.stderr}')
        
        self.stdout.write(f'PostgreSQL database backed up to: {backup_file}')

    def backup_mysql(self, db_config, backup_file):
        """Backup MySQL database using mysqldump"""
        cmd = [
            'mysqldump',
            f"--host={db_config.get('HOST', 'localhost')}",
            f"--port={db_config.get('PORT', 3306)}",
            f"--user={db_config['USER']}",
            f"--password={db_config['PASSWORD']}",
            '--single-transaction',
            '--routines',
            '--triggers',
            db_config['NAME']
        ]
        
        with open(backup_file, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            raise CommandError(f'mysqldump failed: {result.stderr}')
        
        self.stdout.write(f'MySQL database backed up to: {backup_file}')

    def compress_backup(self, backup_file):
        """Compress the backup file using gzip"""
        import gzip
        
        compressed_file = f"{backup_file}.gz"
        
        with open(backup_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Remove original file
        os.remove(backup_file)
        
        self.stdout.write(f'Backup compressed to: {compressed_file}')
