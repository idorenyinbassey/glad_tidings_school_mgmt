#!/usr/bin/env python
"""
Script to create test users for the Glad Tidings School Management System
Creates users with different roles for testing purposes
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.contrib.auth.models import User, Group
from students.models import StudentProfile
from staff.models import StaffProfile
from users.models import CustomUser
from django.utils import timezone

def create_test_users():
    password = "suit272burn754"
    
    print("Creating test users with password:", password)
    print("=" * 50)
    
    # Create Groups if they don't exist
    students_group, _ = Group.objects.get_or_create(name='Students')
    staff_group, _ = Group.objects.get_or_create(name='Staff')
    it_support_group, _ = Group.objects.get_or_create(name='IT Support')
    accountant_group, _ = Group.objects.get_or_create(name='Accountants')
    
    users_created = []
    
    # 1. Create 3 Students
    print("Creating Students...")
    student_data = [
        {
            'username': 'john.doe',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@student.gladtidings.edu',
            'admission_number': 'ST2024001',
            'current_class': 'Grade 10A',
            'guardian_name': 'Robert Doe',
            'guardian_phone': '+234-801-234-5678'
        },
        {
            'username': 'jane.smith',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@student.gladtidings.edu',
            'admission_number': 'ST2024002',
            'current_class': 'Grade 11B',
            'guardian_name': 'Mary Smith',
            'guardian_phone': '+234-802-345-6789'
        },
        {
            'username': 'mike.johnson',
            'first_name': 'Mike',
            'last_name': 'Johnson',
            'email': 'mike.johnson@student.gladtidings.edu',
            'admission_number': 'ST2024003',
            'current_class': 'Grade 9C',
            'guardian_name': 'David Johnson',
            'guardian_phone': '+234-803-456-7890'
        }
    ]
    
    for data in student_data:
        try:
            # Create User
            user, created = CustomUser.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'role': 'student',
                    'is_active': True
                }
            )
            if created:
                user.set_password(password)
                user.save()
            
            # Create Student Profile
            profile, profile_created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'admission_number': data['admission_number'],
                    'guardian_name': data['guardian_name'],
                    'guardian_contact': data['guardian_phone'],
                    'date_of_birth': timezone.datetime(2008, 1, 1).date(),
                    'address': '123 Main Street, Lagos, Nigeria'
                }
            )
            
            # Add to Students group
            user.groups.add(students_group)
            
            users_created.append(f"✓ Student: {user.get_full_name()} ({user.username})")
            print(f"✓ Created student: {user.get_full_name()} - {data['admission_number']}")
            
        except Exception as e:
            print(f"✗ Error creating student {data['username']}: {e}")
    
    # 2. Create 2 Teachers (Staff)
    print("\nCreating Teachers...")
    teacher_data = [
        {
            'username': 'prof.williams',
            'first_name': 'Sarah',
            'last_name': 'Williams',
            'email': 'sarah.williams@gladtidings.edu',
            'staff_id': 'TC2024001',
            'department': 'Mathematics',
            'position': 'Senior Teacher',
            'subjects': 'Mathematics, Physics'
        },
        {
            'username': 'dr.brown',
            'first_name': 'Michael',
            'last_name': 'Brown',
            'email': 'michael.brown@gladtidings.edu',
            'staff_id': 'TC2024002',
            'department': 'English',
            'position': 'Head of Department',
            'subjects': 'English Language, Literature'
        }
    ]
    
    for data in teacher_data:
        try:
            # Create User
            user, created = CustomUser.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'role': 'staff',
                    'is_active': True
                }
            )
            if created:
                user.set_password(password)
                user.save()
            
            # Create Staff Profile
            profile, profile_created = StaffProfile.objects.get_or_create(
                user=user,
                defaults={
                    'staff_id': data['staff_id'],
                    'department': 'science' if data['department'] == 'Mathematics' else 'arts',
                    'position': 'teacher',
                    'phone': '+234-805-123-4567',
                    'address': '456 Teacher Avenue, Abuja, Nigeria'
                }
            )
            
            # Add to Staff group
            user.groups.add(staff_group)
            
            users_created.append(f"✓ Teacher: {user.get_full_name()} ({user.username}) - {data['department']}")
            print(f"✓ Created teacher: {user.get_full_name()} - {data['department']}")
            
        except Exception as e:
            print(f"✗ Error creating teacher {data['username']}: {e}")
    
    # 3. Create 1 IT Support
    print("\nCreating IT Support...")
    try:
        user, created = CustomUser.objects.get_or_create(
            username='tech.admin',
            defaults={
                'first_name': 'Alex',
                'last_name': 'Tech',
                'email': 'alex.tech@gladtidings.edu',
                'role': 'it_support',
                'is_active': True
            }
        )
        if created:
            user.set_password(password)
            user.save()
        
        # Create Staff Profile for IT Support
        profile, profile_created = StaffProfile.objects.get_or_create(
            user=user,
            defaults={
                'staff_id': 'IT2024001',
                'department': 'it',
                'position': 'it_support',
                'phone': '+234-806-789-0123',
                'address': '789 Tech Street, Port Harcourt, Nigeria'
            }
        )
        
        # Add to IT Support group
        user.groups.add(it_support_group)
        
        users_created.append(f"✓ IT Support: {user.get_full_name()} ({user.username})")
        print(f"✓ Created IT Support: {user.get_full_name()}")
        
    except Exception as e:
        print(f"✗ Error creating IT support: {e}")
    
    # 4. Create 1 Accountant
    print("\nCreating Accountant...")
    try:
        user, created = CustomUser.objects.get_or_create(
            username='finance.manager',
            defaults={
                'first_name': 'Grace',
                'last_name': 'Accounts',
                'email': 'grace.accounts@gladtidings.edu',
                'role': 'accountant',
                'is_active': True
            }
        )
        if created:
            user.set_password(password)
            user.save()
        
        # Create Staff Profile for Accountant
        profile, profile_created = StaffProfile.objects.get_or_create(
            user=user,
            defaults={
                'staff_id': 'AC2024001',
                'department': 'accounts',
                'position': 'accountant',
                'phone': '+234-807-890-1234',
                'address': '321 Finance Plaza, Kano, Nigeria'
            }
        )
        
        # Add to Accountants group
        user.groups.add(accountant_group)
        
        users_created.append(f"✓ Accountant: {user.get_full_name()} ({user.username})")
        print(f"✓ Created Accountant: {user.get_full_name()}")
        
    except Exception as e:
        print(f"✗ Error creating accountant: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 TEST USERS CREATED SUCCESSFULLY!")
    print("=" * 50)
    print(f"Password for all users: {password}")
    print("\nUsers created:")
    for user in users_created:
        print(user)
    
    print("\n📋 LOGIN DETAILS:")
    print("-" * 30)
    print("STUDENTS:")
    print("• john.doe (John Doe - Grade 10A)")
    print("• jane.smith (Jane Smith - Grade 11B)")  
    print("• mike.johnson (Mike Johnson - Grade 9C)")
    print("\nTEACHERS:")
    print("• prof.williams (Sarah Williams - Mathematics)")
    print("• dr.brown (Michael Brown - English)")
    print("\nIT SUPPORT:")
    print("• tech.admin (Alex Tech)")
    print("\nACCOUNTANT:")
    print("• finance.manager (Grace Accounts)")
    print(f"\nPassword: {password}")
    print("\n🌐 Access the system at: http://127.0.0.1:8000/")

if __name__ == "__main__":
    create_test_users()
