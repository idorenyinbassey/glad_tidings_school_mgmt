#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
    
    try:
        django.setup()
        
        # Run academics migration
        print("Running academics migration...")
        execute_from_command_line(['manage.py', 'migrate', 'academics', '0002'])
        
        # Run CBT migration
        print("Running CBT migration...")
        execute_from_command_line(['manage.py', 'migrate', 'cbt', '0002'])
        
        print("All migrations completed successfully!")
        
    except Exception as e:
        print(f"Error running migrations: {e}")
        sys.exit(1)
