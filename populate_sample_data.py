#!/usr/bin/env python
"""
Populate test data for the school management system
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Add the project root to Python path
sys.path.append('/c/Users/Idorenyin/Desktop/Projects/glad_tidings_school_mgmt')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.contrib.auth.models import User
from students.models import Student
from staff.models import Staff
from accounting.models import TuitionFee, Payment, Expense, Payroll
from django.utils import timezone

def create_sample_data():
    print("Creating sample data...")
    
    # Create admin user if not exists
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'admin@gladtidingsschool.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"Created admin user: {admin_user.username}")
    
    # Create sample students
    for i in range(1, 21):  # 20 students
        user, created = User.objects.get_or_create(
            username=f'student{i}',
            defaults={
                'first_name': f'Student{i}',
                'last_name': f'Test',
                'email': f'student{i}@test.com'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            
            # Create student profile
            student, created = Student.objects.get_or_create(
                user=user,
                defaults={
                    'admission_number': f'ST{2024}{i:03d}',
                    'current_class': f'Grade {(i % 12) + 1}',
                    'date_of_birth': datetime(2005 + (i % 10), (i % 12) + 1, (i % 28) + 1).date(),
                    'gender': 'male' if i % 2 == 0 else 'female',
                    'phone_number': f'080{i:08d}',
                    'address': f'{i} Test Street, Lagos'
                }
            )
            if created:
                print(f"Created student: {student.user.get_full_name()}")
    
    # Create sample staff
    for i in range(1, 11):  # 10 staff members
        user, created = User.objects.get_or_create(
            username=f'staff{i}',
            defaults={
                'first_name': f'Staff{i}',
                'last_name': f'Teacher',
                'email': f'staff{i}@test.com'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            
            # Create staff profile
            staff, created = Staff.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': f'EMP{2024}{i:03d}',
                    'department': 'Academic' if i % 2 == 0 else 'Administration',
                    'position': 'Teacher' if i % 2 == 0 else 'Administrator',
                    'date_joined': timezone.now().date() - timedelta(days=i*30),
                    'phone_number': f'070{i:08d}',
                    'address': f'{i} Staff Avenue, Lagos',
                    'basic_salary': Decimal('80000') + (Decimal('10000') * i)
                }
            )
            if created:
                print(f"Created staff: {staff.user.get_full_name()}")
    
    # Create tuition fees for students
    students = Student.objects.all()
    for student in students:
        fee, created = TuitionFee.objects.get_or_create(
            student=student,
            session='2024/2025',
            term='First',
            defaults={
                'amount_due': Decimal('50000'),
                'amount_paid': Decimal('0'),
                'due_date': timezone.now().date() + timedelta(days=30),
                'status': 'unpaid'
            }
        )
        if created:
            print(f"Created tuition fee for: {student.user.get_full_name()}")
    
    # Create some payments
    tuition_fees = TuitionFee.objects.all()[:15]  # First 15 students pay
    for i, fee in enumerate(tuition_fees):
        payment_amount = Decimal('25000') if i < 10 else Decimal('50000')
        payment, created = Payment.objects.get_or_create(
            student=fee.student,
            amount=payment_amount,
            defaults={
                'payment_date': timezone.now().date() - timedelta(days=i*2),
                'method': 'bank_transfer' if i % 2 == 0 else 'cash',
                'reference': f'PAY{2024}{i+1:04d}',
                'description': f'Tuition fee payment - {fee.session} {fee.term}'
            }
        )
        if created:
            # Update tuition fee
            fee.amount_paid += payment_amount
            if fee.amount_paid >= fee.amount_due:
                fee.status = 'paid'
            else:
                fee.status = 'partial'
            fee.save()
            print(f"Created payment: {payment.reference}")
    
    # Create expenses
    expense_categories = ['supplies', 'maintenance', 'salary', 'utility', 'other']
    for i in range(1, 26):  # 25 expenses
        expense, created = Expense.objects.get_or_create(
            description=f'Test expense {i}',
            defaults={
                'amount': Decimal('5000') + (Decimal('1000') * (i % 10)),
                'category': expense_categories[i % len(expense_categories)],
                'date': timezone.now().date() - timedelta(days=i*3),
                'vendor': f'Vendor {i}',
                'receipt_number': f'RCT{2024}{i:04d}'
            }
        )
        if created:
            print(f"Created expense: {expense.description}")
    
    # Create payroll for staff
    staff_members = Staff.objects.all()
    current_month = timezone.now().strftime('%B')
    current_year = timezone.now().year
    
    for staff in staff_members:
        payroll, created = Payroll.objects.get_or_create(
            staff=staff,
            month=current_month,
            year=current_year,
            defaults={
                'basic_salary': staff.basic_salary or Decimal('80000'),
                'allowances': Decimal('10000'),
                'deductions': Decimal('5000'),
                'amount': (staff.basic_salary or Decimal('80000')) + Decimal('10000') - Decimal('5000'),
                'paid': False
            }
        )
        if created:
            print(f"Created payroll for: {staff.user.get_full_name()}")
    
    print("\nSample data creation completed!")
    print(f"Students: {Student.objects.count()}")
    print(f"Staff: {Staff.objects.count()}")
    print(f"Tuition Fees: {TuitionFee.objects.count()}")
    print(f"Payments: {Payment.objects.count()}")
    print(f"Expenses: {Expense.objects.count()}")
    print(f"Payroll: {Payroll.objects.count()}")

if __name__ == '__main__':
    create_sample_data()
