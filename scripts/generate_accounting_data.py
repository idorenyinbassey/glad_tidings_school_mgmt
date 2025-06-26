"""
Script to generate sample accounting data for testing.
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_management.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from accounting.models import TuitionFee, Payment, Expense
from students.models import StudentProfile, AcademicStatus

User = get_user_model()

def create_sample_data():
    """Create sample accounting data for testing."""
    
    # Check if we already have data
    if TuitionFee.objects.count() > 0 and Payment.objects.count() > 0 and Expense.objects.count() > 0:
        print("Data already exists. Skipping sample data creation.")
        return
    
    # Get an admin user (or create one)
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@gladschool.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print("Created admin user.")
    
    # Check if we have student profiles
    if StudentProfile.objects.count() == 0:
        print("No students found. Creating sample students...")
        # Create sample students
        for i in range(1, 11):
            user = User.objects.create_user(
                username=f'student{i}',
                email=f'student{i}@gladschool.com',
                password='student123',
                first_name=f'Student{i}',
                last_name='Sample',
                role='student'
            )
            
            student = StudentProfile.objects.create(
                user=user,
                admission_number=f'STU-2025-{i:03d}',
                date_of_birth=timezone.now() - timedelta(days=365*10),
                guardian_name='Parent Name',
                guardian_contact='0123456789'
            )
            
            # Create academic status
            AcademicStatus.objects.create(
                student=student,
                session='2025/2026',
                term='1st Term',
                current_class=random.choice(['Primary 1', 'Primary 2', 'Primary 3', 'Primary 4', 'Primary 5', 'Primary 6', 
                                           'JSS 1', 'JSS 2', 'JSS 3', 'SS 1', 'SS 2', 'SS 3']),
                promoted=False
            )
            
            print(f"Created student: {student}")
    
    # Create tuition fees for each student
    print("Creating tuition fees...")
    for student in StudentProfile.objects.all():
        # Skip if student already has tuition fees
        if TuitionFee.objects.filter(student=student).exists():
            continue
        
        # Get the class level to determine fee amount
        academic_status = AcademicStatus.objects.filter(student=student).first()
        if not academic_status:
            continue
            
        class_level = academic_status.current_class
        
        # Determine fee amount based on class level
        if class_level.startswith('Pre-Nursery') or class_level.startswith('Nursery'):
            amount = Decimal('180000')
        elif class_level.startswith('Primary'):
            amount = Decimal('200000')
        elif class_level.startswith('JSS'):
            amount = Decimal('250000')
        else:  # SS classes
            amount = Decimal('280000')
        
        # Create tuition fee record
        tuition_fee = TuitionFee.objects.create(
            student=student,
            session='2025/2026',
            term='1st Term',
            amount_due=amount,
            amount_paid=Decimal('0'),
            due_date=timezone.now() + timedelta(days=30),
            status='unpaid',
            created_by=admin_user
        )
        
        # Randomly decide if payment has been made
        payment_status = random.choice(['paid', 'partial', 'unpaid'])
        
        if payment_status == 'paid':
            # Full payment
            payment_amount = amount
            Payment.objects.create(
                tuition_fee=tuition_fee,
                amount=payment_amount,
                payment_date=timezone.now() - timedelta(days=random.randint(1, 10)),
                method=random.choice(['cash', 'bank', 'card', 'online']),
                receipt_number=f'RCP-{random.randint(10000, 99999)}',
                reference=f'REF-{random.randint(100000, 999999)}',
                notes='Full payment',
                created_by=admin_user
            )
            print(f"Created full payment for {student}")
            
        elif payment_status == 'partial':
            # Partial payment (40-80% of full amount)
            payment_percentage = random.uniform(0.4, 0.8)
            payment_amount = amount * Decimal(payment_percentage)
            Payment.objects.create(
                tuition_fee=tuition_fee,
                amount=payment_amount,
                payment_date=timezone.now() - timedelta(days=random.randint(1, 10)),
                method=random.choice(['cash', 'bank', 'card', 'online']),
                receipt_number=f'RCP-{random.randint(10000, 99999)}',
                reference=f'REF-{random.randint(100000, 999999)}',
                notes='Partial payment',
                created_by=admin_user
            )
            print(f"Created partial payment for {student}")
    
    # Create sample expenses
    print("Creating sample expenses...")
    expense_categories = ['supplies', 'maintenance', 'salary', 'utility', 'other']
    expense_descriptions = {
        'supplies': ['School Supplies', 'Office Supplies', 'Classroom Materials', 'Laboratory Equipment'],
        'maintenance': ['Building Repairs', 'Plumbing Work', 'Electrical Repairs', 'Ground Maintenance'],
        'salary': ['Teacher Salaries', 'Administrative Staff Salaries', 'Support Staff Wages', 'Bonus Payments'],
        'utility': ['Electricity Bills', 'Water Bills', 'Internet Services', 'Phone Bills'],
        'other': ['Transport Costs', 'Event Expenses', 'Miscellaneous', 'External Services']
    }
    
    # Create expenses for the last 6 months
    for i in range(30):  # 30 expense entries
        category = random.choice(expense_categories)
        description = random.choice(expense_descriptions[category])
        
        # Amount based on category
        if category == 'salary':
            amount = Decimal(random.uniform(50000, 250000))
        elif category == 'utility':
            amount = Decimal(random.uniform(30000, 100000))
        elif category == 'maintenance':
            amount = Decimal(random.uniform(20000, 120000))
        elif category == 'supplies':
            amount = Decimal(random.uniform(10000, 80000))
        else:  # other
            amount = Decimal(random.uniform(5000, 50000))
        
        # Date within last 6 months
        date = timezone.now() - timedelta(days=random.randint(1, 180))
        
        Expense.objects.create(
            description=description,
            amount=amount,
            date=date,
            category=category,
            created_by=admin_user
        )
    
    print(f"Created {Expense.objects.count()} expense records")
    
    print("Sample accounting data created successfully!")

if __name__ == "__main__":
    create_sample_data()
