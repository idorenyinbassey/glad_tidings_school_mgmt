#!/usr/bin/env python
"""
Management command to add users with specific roles to the Glad Tidings School Portal.
This script can be used to add individual users or bulk import from CSV files.
"""

import os
import sys
import csv
import argparse
import django
from django.conf import settings
from django.contrib.auth import get_user_model

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

# Now we can import Django models
from django.contrib.auth.models import Group
from users.models import CustomUser

def create_user(username, email, password, first_name, last_name, role):
    """Create a user with the specified role"""
    User = get_user_model()
    
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        print(f"User {username} already exists. Skipping.")
        return None
    
    # Create user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    # Set role
    valid_roles = ['student', 'staff', 'admin', 'it_support']
    if role in valid_roles:
        user.role = role
        # If admin, set is_staff to True to allow admin site access
        if role == 'admin':
            user.is_staff = True
    else:
        print(f"Warning: Invalid role '{role}'. Setting to default 'student'.")
        user.role = 'student'
    
    # Save user
    user.save()
    print(f"User {username} created successfully with role {user.role}.")
    return user

def import_from_csv(csv_file):
    """Import multiple users from a CSV file"""
    created_users = 0
    skipped_users = 0
    
    try:
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Check for required fields
                    username = row.get('username')
                    email = row.get('email', '')
                    password = row.get('password')
                    first_name = row.get('first_name', '')
                    last_name = row.get('last_name', '')
                    role = row.get('role', 'student').lower()
                    
                    if username and password:
                        user = create_user(
                            username=username,
                            email=email,
                            password=password,
                            first_name=first_name,
                            last_name=last_name,
                            role=role
                        )
                        if user:
                            created_users += 1
                        else:
                            skipped_users += 1
                    else:
                        print(f"Error: Missing required fields (username or password) in row {reader.line_num}")
                        skipped_users += 1
                except Exception as e:
                    print(f"Error processing row: {e}")
                    skipped_users += 1
                    
    except Exception as e:
        print(f"Error opening or reading CSV file: {e}")
        return 0, 0
    
    return created_users, skipped_users

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Add users to Glad Tidings School Portal.')
    
    # Add arguments
    parser.add_argument('--add', action='store_true', help='Add a single user')
    parser.add_argument('--import-csv', type=str, help='Import users from CSV file')
    parser.add_argument('--username', type=str, help='Username for the user')
    parser.add_argument('--email', type=str, help='Email address')
    parser.add_argument('--password', type=str, help='Password')
    parser.add_argument('--first-name', type=str, help='First name')
    parser.add_argument('--last-name', type=str, help='Last name')
    parser.add_argument('--role', type=str, choices=['student', 'staff', 'admin', 'it_support'], 
                        default='student', help='User role')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Process commands
    if args.add:
        # Check required fields
        if not args.username or not args.password:
            print("Error: Username and password are required")
            parser.print_help()
            return
        
        # Create single user
        user = create_user(
            username=args.username,
            email=args.email or '',
            password=args.password,
            first_name=args.first_name or '',
            last_name=args.last_name or '',
            role=args.role
        )
        
        if user:
            print("User added successfully!")
    
    elif args.import_csv:
        # Import from CSV
        if not os.path.isfile(args.import_csv):
            print(f"Error: CSV file not found: {args.import_csv}")
            return
        
        created, skipped = import_from_csv(args.import_csv)
        print(f"\nImport completed: {created} users created, {skipped} users skipped")
    
    else:
        # No command specified
        parser.print_help()

if __name__ == "__main__":
    main()
