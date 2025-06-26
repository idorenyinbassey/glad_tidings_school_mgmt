"""
Script to create an accountant staff user and add some accounting records
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
from accounting.models import TuitionFee, Payment, Expense

User = get_user_model()

def create_accountant():
    """Create a staff user with accountant role"""
    try:
        # Check if user already exists
        if User.objects.filter(username='accountant').exists():
            print("Accountant user already exists.")
            return User.objects.get(username='accountant')
        
        # Create user
        user = User.objects.create_user(
            username='accountant',
            email='accountant@gladtidingsschool.example',
            password='AccountPass123!',
            first_name='Finance',
            last_name='Officer',
            role='staff',
        )
        
        # Create staff profile
        profile = StaffProfile.objects.create(
            user=user,
            staff_id='STAFF-ACC-001',
            position='accountant',
            department='accounts',
            phone='08012345678',
            address='123 Finance Street, School District',
        )
        
        print(f"Created accountant user: {user.username} with staff ID: {profile.staff_id}")
        return user
    except Exception as e:
        print(f"Error creating accountant: {e}")
        traceback.print_exc()
        return None

def get_or_create_students(num_students=5):
    """Get existing students or create new ones if needed"""
    try:
        existing_students = StudentProfile.objects.all()
        
        if existing_students.count() >= num_students:
            return list(existing_students[:num_students])
        
        students = list(existing_students)
        students_needed = num_students - len(students)
        
        # Create additional students if needed
        for i in range(students_needed):
            student_number = len(students) + i + 1
            user = User.objects.create_user(
                username=f'student{student_number}',
                email=f'student{student_number}@gladtidingsschool.example',
                password='Student123!',
                first_name=f'Student{student_number}',
                last_name='Lastname',
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
        print(f"Error getting/creating students: {e}")
        traceback.print_exc()
        return []

def create_tuition_fees(accountant, students):
    """Create tuition fees for students"""
    try:
        current_session = "2025/2026"
        current_term = "First Term"
        
        tuition_fees = []
        
        for student in students:
            try:
                # Check if fee already exists for this student, session and term
                if TuitionFee.objects.filter(
                    student=student,
                    session=current_session,
                    term=current_term
                ).exists():
                    fee = TuitionFee.objects.get(
                        student=student,
                        session=current_session,
                        term=current_term
                    )
                    tuition_fees.append(fee)
                    print(f"Tuition fee already exists for {student}")
                    continue
                
                # Random amount between 200,000 and 400,000
                amount_due = Decimal(random.randint(2000, 4000) * 100)
                
                fee = TuitionFee.objects.create(
                    student=student,
                    session=current_session,
                    term=current_term,
                    amount_due=amount_due,
                    amount_paid=0,
                    due_date=timezone.now().date() + datetime.timedelta(days=30),
                    status='unpaid',  # Set this explicitly
                    created_by=accountant,
                )
                
                tuition_fees.append(fee)
                print(f"Created tuition fee for {student}: ₦{amount_due:,}")
            except Exception as e:
                print(f"Error creating fee for {student}: {e}")
                traceback.print_exc()
        
        return tuition_fees
    except Exception as e:
        print(f"Error in create_tuition_fees: {e}")
        traceback.print_exc()
        return []

def record_payments(accountant, tuition_fees):
    """Record payments for some tuition fees"""
    try:
        payment_methods = ['cash', 'bank', 'card', 'online']
        
        for fee in tuition_fees:
            try:
                # Check if this fee already has payments
                existing_payments = Payment.objects.filter(tuition_fee=fee).count()
                if existing_payments > 0:
                    print(f"Payments already exist for {fee.student}, skipping")
                    continue
                
                # Random decision: full payment, partial payment, or no payment
                payment_type = random.choice(['full', 'partial', 'none'])
                
                if payment_type == 'none':
                    print(f"No payment recorded for {fee.student}")
                    continue
                
                # Calculate remaining amount due
                remaining_due = fee.amount_due - fee.amount_paid
                
                if payment_type == 'full':
                    amount = remaining_due
                else:  # partial
                    # Pay between 30% and 70% of the remaining fee
                    percentage = Decimal(random.uniform(0.3, 0.7))
                    amount = int(remaining_due * percentage)
                
                # Record the payment
                payment = Payment.objects.create(
                    tuition_fee=fee,
                    amount=amount,
                    payment_date=timezone.now().date() - datetime.timedelta(days=random.randint(0, 14)),
                    method=random.choice(payment_methods),
                    receipt_number=f"RCP-{timezone.now().year}-{random.randint(1000, 9999)}",
                    reference=f"REF-{fee.student.admission_number}-{timezone.now().strftime('%m%d')}",
                    notes=f"Payment for {fee.session} {fee.term}",
                    created_by=accountant,
                )
                
                print(f"Recorded payment of ₦{amount:,} for {fee.student} via {payment.method}")
            except Exception as e:
                print(f"Error recording payment for {fee.student}: {e}")
                traceback.print_exc()
    except Exception as e:
        print(f"Error in record_payments: {e}")
        traceback.print_exc()

def create_expenses(accountant, num_expenses=10):
    """Create some expenses"""
    try:
        categories = ['supplies', 'maintenance', 'salary', 'utility', 'other']
        descriptions = {
            'supplies': ['Stationery', 'Lab Equipment', 'Books', 'Uniforms', 'Sports Equipment'],
            'maintenance': ['Building Repair', 'AC Maintenance', 'Plumbing Work', 'Electrical Repair', 'Painting'],
            'salary': ['Staff Salary', 'Bonuses', 'Overtime Pay', 'Contract Worker Payment'],
            'utility': ['Electricity Bill', 'Water Bill', 'Internet Service', 'Phone Bills', 'Waste Management'],
            'other': ['Transport', 'Events', 'Advertisements', 'Insurance', 'Miscellaneous']
        }
        
        for _ in range(num_expenses):
            try:
                category = random.choice(categories)
                description = random.choice(descriptions[category])
                
                # Amount between 10,000 and 500,000
                amount = Decimal(random.randint(100, 5000) * 100)
                
                # Date within the last 90 days
                date = timezone.now().date() - datetime.timedelta(days=random.randint(0, 90))
                
                expense = Expense.objects.create(
                    description=f"{description} - {date.strftime('%b %Y')}",
                    amount=amount,
                    date=date,
                    category=category,
                    created_by=accountant,
                )
                
                print(f"Created expense: {expense.description} - ₦{amount:,}")
            except Exception as e:
                print(f"Error creating expense: {e}")
                traceback.print_exc()
    except Exception as e:
        print(f"Error in create_expenses: {e}")
        traceback.print_exc()

def main():
    """Main function"""
    try:
        print("Creating accountant staff user...")
        accountant = create_accountant()
        if not accountant:
            print("Failed to create or retrieve accountant user.")
            return
        
        print("\nGetting/creating students...")
        students = get_or_create_students(num_students=5)
        if not students:
            print("Failed to get or create students.")
            return
        
        print("\nCreating tuition fees...")
        tuition_fees = create_tuition_fees(accountant, students)
        
        print("\nRecording payments...")
        record_payments(accountant, tuition_fees)
        
        print("\nCreating expenses...")
        create_expenses(accountant, num_expenses=10)
        
        print("\nDone! You can now log in with the following credentials:")
        print("Username: accountant")
        print("Password: AccountPass123!")
    except Exception as e:
        print(f"Error in main function: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
