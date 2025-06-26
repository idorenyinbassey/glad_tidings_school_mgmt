"""
Script to create more students with tuition fees and payments
"""

import os
import django
import sys
import random
import datetime
import traceback
from decimal import Decimal

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from staff.models import StaffProfile
from students.models import StudentProfile
from accounting.models import TuitionFee, Payment

User = get_user_model()

def get_accountant():
    """Get the accountant user"""
    try:
        # Check if user exists
        if User.objects.filter(username='accountant').exists():
            return User.objects.get(username='accountant')
        else:
            print("Accountant user doesn't exist. Please run create_accounting_data_improved.py first.")
            return None
    except Exception as e:
        print(f"Error getting accountant: {e}")
        traceback.print_exc()
        return None

def create_new_students(start_num=10, num_students=3):
    """Create additional students"""
    try:
        students = []
        
        # Create new students
        for i in range(num_students):
            student_number = start_num + i
            username = f'student{student_number}'
            
            # Skip if user already exists
            if User.objects.filter(username=username).exists():
                print(f"Student {username} already exists, skipping")
                continue
            
            user = User.objects.create_user(
                username=username,
                email=f'{username}@gladtidingsschool.example',
                password='Student123!',
                first_name=f'Student{student_number}',
                last_name='New',
                role='student',
            )
            
            # Create student profile
            profile = StudentProfile.objects.create(
                user=user,
                admission_number=f'STU-2025-{student_number:03d}',
                date_of_birth=datetime.date(2010, 1, 1) - datetime.timedelta(days=random.randint(0, 1825)),
                address=f'{student_number} Student Street, School District',
                guardian_name='Parent Name',
                guardian_contact='080987654321',
            )
            
            students.append(profile)
            print(f"Created student: {user.username} with admission number: {profile.admission_number}")
        
        return students
    except Exception as e:
        print(f"Error creating students: {e}")
        traceback.print_exc()
        return []

def create_fees_and_payments(accountant, students):
    """Create tuition fees and payments for students"""
    try:
        current_session = "2025/2026"
        current_term = "First Term"
        payment_methods = ['cash', 'bank', 'card', 'online']
        
        for student in students:
            try:
                # Create fee
                amount_due = Decimal(random.randint(2000, 4000) * 100)
                
                fee = TuitionFee.objects.create(
                    student=student,
                    session=current_session,
                    term=current_term,
                    amount_due=amount_due,
                    amount_paid=0,
                    due_date=timezone.now().date() + datetime.timedelta(days=30),
                    status='unpaid',
                    created_by=accountant,
                )
                
                print(f"Created tuition fee for {student}: ₦{amount_due:,}")
                
                # Random decision: full payment, partial payment, or no payment
                payment_type = random.choice(['full', 'partial', 'none'])
                
                if payment_type == 'none':
                    print(f"No payment recorded for {student}")
                    continue
                
                if payment_type == 'full':
                    amount = amount_due
                else:  # partial
                    # Pay between 30% and 70% of the fee
                    percentage = Decimal(random.uniform(0.3, 0.7))
                    amount = int(amount_due * percentage)
                
                # Record the payment
                payment = Payment.objects.create(
                    tuition_fee=fee,
                    amount=amount,
                    payment_date=timezone.now().date() - datetime.timedelta(days=random.randint(0, 14)),
                    method=random.choice(payment_methods),
                    receipt_number=f"RCP-{timezone.now().year}-{random.randint(1000, 9999)}",
                    reference=f"REF-{student.admission_number}-{timezone.now().strftime('%m%d')}",
                    notes=f"Payment for {fee.session} {fee.term}",
                    created_by=accountant,
                )
                
                print(f"Recorded payment of ₦{amount:,} for {student} via {payment.method}")
                
                # Verify that the status was updated correctly
                fee.refresh_from_db()
                print(f"Fee status: {fee.status}, Amount paid: ₦{fee.amount_paid:,} of ₦{fee.amount_due:,}")
                
            except Exception as e:
                print(f"Error creating fee/payment for {student}: {e}")
                traceback.print_exc()
    except Exception as e:
        print(f"Error in create_fees_and_payments: {e}")
        traceback.print_exc()

def main():
    """Main function"""
    try:
        print("Getting accountant user...")
        accountant = get_accountant()
        if not accountant:
            return
        
        print("\nCreating new students...")
        students = create_new_students(start_num=10, num_students=3)
        if not students:
            print("Failed to create new students.")
            return
        
        print("\nCreating fees and recording payments...")
        create_fees_and_payments(accountant, students)
        
        print("\nDone! New students created with fees and payments.")
    except Exception as e:
        print(f"Error in main function: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
