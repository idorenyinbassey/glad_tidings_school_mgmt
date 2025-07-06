#!/usr/bin/env python
"""
Simple migration script for accounting app
"""
import os
import sys
import django
from django.core.management import call_command

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
    django.setup()

def create_accounting_migrations():
    """Create and run accounting migrations"""
    try:
        setup_django()
        
        print("Creating migrations for accounting app...")
        call_command('makemigrations', 'accounting', verbosity=2)
        
        print("Running migrations for accounting app...")
        call_command('migrate', 'accounting', verbosity=2)
        
        print("Accounting migrations completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = create_accounting_migrations()
    if not success:
        sys.exit(1)
