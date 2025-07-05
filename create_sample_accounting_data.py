#!/usr/bin/env python
"""
Create sample accounting data to populate the templates
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from accounting.models import TuitionFee, Payment, Expense, Payroll
from students.models import StudentProfile
from staff.models import StaffProfile
from users.models import CustomUser
from django.utils import timezone

def create_sample_accounting_data():
    """Create sample data for accounting templates"""
    print("🏦 Creating sample accounting data...")
    
    # Create some students if they don't exist
    for i in range(1, 6):
        user, created = CustomUser.objects.get_or_create(
            username=f'student{i}',
            defaults={
                'first_name': f'Student{i}',
                'last_name': 'Test',
                'email': f'student{i}@test.com',
                'role': 'student'
            }
        )
        if created:
            user.set_password('student123')
            user.save()
        
        student_profile, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'admission_number': f'ST2024{i:03d}',
                'date_of_birth': datetime(2005, 1, 1).date()
            }
        )
        if created:
            print(f"Created student: {student_profile.admission_number}")
    
    # Create some staff for payroll
    for i in range(1, 4):
        user, created = CustomUser.objects.get_or_create(
            username=f'staff{i}',
            defaults={
                'first_name': f'Staff{i}',
                'last_name': 'Member',
                'email': f'staff{i}@test.com',
                'role': 'staff'
            }
        )
        if created:
            user.set_password('staff123')
            user.save()
        
        staff_profile, created = StaffProfile.objects.get_or_create(
            user=user,
            defaults={
                'staff_id': f'EMP{i:03d}',
                'position': 'teacher',
                'department': 'academics'
            }
        )
        if created:
            print(f"Created staff: {staff_profile.staff_id}")
    
    # Create tuition fees
    students = StudentProfile.objects.all()[:5]
    admin_user = CustomUser.objects.filter(role='admin').first()
    
    for i, student in enumerate(students, 1):
        fee, created = TuitionFee.objects.get_or_create(
            student=student,
            session='2024/2025',
            term='First',
            defaults={
                'amount_due': Decimal(100000 + (i * 10000)),
                'due_date': timezone.now().date() + timedelta(days=30),
                'created_by': admin_user
            }
        )
        if created:
            print(f"Created tuition fee for {student.admission_number}: ₦{fee.amount_due}")
    
    # Create some payments
    fees = TuitionFee.objects.all()[:3]
    for i, fee in enumerate(fees, 1):
        payment, created = Payment.objects.get_or_create(
            tuition_fee=fee,
            amount=Decimal(50000),
            defaults={
                'payment_date': timezone.now().date() - timedelta(days=i*2),
                'method': 'bank_transfer',
                'receipt_number': f'RCP{i:04d}',
                'reference': f'TXN{i:06d}',
                'created_by': admin_user
            }
        )
        if created:
            print(f"Created payment: ₦{payment.amount} for {fee.student.admission_number}")
    
    # Create expenses
    expense_data = [
        ('Office supplies', 'supplies', 25000, 'Stationery and office materials'),
        ('Electricity bill', 'utility', 45000, 'Monthly electricity payment'),
        ('Internet service', 'utility', 15000, 'Monthly internet subscription'),
        ('Maintenance repair', 'maintenance', 30000, 'Classroom repairs'),
        ('Staff training', 'other', 20000, 'Professional development'),
    ]
    
    for desc, category, amount, details in expense_data:
        expense, created = Expense.objects.get_or_create(
            description=desc,
            defaults={
                'category': category,
                'amount': Decimal(amount),
                'date': timezone.now().date() - timedelta(days=len(expense_data)),
                'created_by': admin_user
            }
        )
        if created:
            print(f"Created expense: {desc} - ₦{amount}")
    
    # Create payroll entries
    staff_members = StaffProfile.objects.all()[:3]
    for i, staff in enumerate(staff_members, 1):
        payroll, created = Payroll.objects.get_or_create(
            staff=staff,
            month=timezone.now().date().replace(day=1),
            defaults={
                'basic_salary': Decimal(80000 + (i * 10000)),
                'allowances': Decimal(15000),
                'deductions': Decimal(5000),
                'created_by': admin_user
            }
        )
        if created:
            print(f"Created payroll for {staff.staff_id}: ₦{payroll.net_salary}")
    
    print("✅ Sample accounting data created successfully!")
    
    # Print summary
    print(f"\n📊 Data Summary:")
    print(f"Students: {StudentProfile.objects.count()}")
    print(f"Staff: {StaffProfile.objects.count()}")
    print(f"Tuition Fees: {TuitionFee.objects.count()}")
    print(f"Payments: {Payment.objects.count()}")
    print(f"Expenses: {Expense.objects.count()}")
    print(f"Payroll Entries: {Payroll.objects.count()}")

if __name__ == '__main__':
    create_sample_accounting_data()
