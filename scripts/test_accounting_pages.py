import os
import sys
import django
import datetime
import random
from decimal import Decimal

# Set up Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_tidings_school_mgmt.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth import get_user_model
from students.models import StudentProfile
from accounting.models import TuitionFee, Payment, Expense, Payroll
from staff.models import StaffProfile

User = get_user_model()

def print_separator():
    print("\n" + "="*80 + "\n")

def create_test_data():
    """Create test data for accounting module"""
    print("Starting test data creation for accounting module...")
    
    # Create sample students if they don't exist
    students_data = []
    classes = ['Nursery 1', 'Primary 3', 'Primary 6', 'JSS 1', 'JSS 3', 'SS 2']
    
    for i in range(1, 6):
        username = f"student{i}"
        try:
            user = User.objects.get(username=username)
            student = user.student_profile
            print(f"Found existing student: {student}")
        except (User.DoesNotExist, AttributeError):
            # Create new student
            user = User.objects.create_user(
                username=username,
                email=f"student{i}@example.com",
                password="password123",
                first_name=f"Student{i}",
                last_name=f"Lastname{i}",
                role="student"
            )
            
            student = StudentProfile.objects.create(
                user=user,
                admission_number=f"STU-2025-{100+i}",
                date_of_birth=datetime.date(2010, 1, i),
                address=f"Address for Student {i}",
                guardian_name=f"Guardian {i}",
                guardian_contact=f"080123456{i}0"
            )
            print(f"Created student: {student}")
            
        students_data.append(student)
    
    # Create tuition fees
    print("\nCreating tuition fees...")
    fee_amounts = {
        'Nursery 1': Decimal('180000.00'),
        'Primary 3': Decimal('200000.00'),
        'Primary 6': Decimal('220000.00'),
        'JSS 1': Decimal('250000.00'),
        'JSS 3': Decimal('250000.00'),
        'SS 2': Decimal('280000.00')
    }
    
    current_session = "2024/2025"
    current_term = "3rd Term"
    
    # Find an admin or staff user for created_by field
    try:
        admin_user = User.objects.filter(role__in=['admin', 'staff']).first()
        if not admin_user:
            admin_user = User.objects.filter(is_staff=True).first()
    except:
        admin_user = None
    
    created_fees = []
    
    for i, student in enumerate(students_data):
        # Assign a class to the student
        class_level = classes[i % len(classes)]
        amount = fee_amounts.get(class_level, Decimal('200000.00'))
        
        # Check if fee already exists
        existing_fee = TuitionFee.objects.filter(
            student=student,
            session=current_session,
            term=current_term
        ).first()
        
        if existing_fee:
            print(f"Fee already exists for {student}: {existing_fee}")
            created_fees.append(existing_fee)
            continue
        
        # Create fee with random status
        status_choice = random.choice(['unpaid', 'partial', 'paid'])
        amount_paid = Decimal('0.00')
        paid_date = None
        
        if status_choice == 'partial':
            # Pay between 30% and 70%
            percent_paid = random.uniform(0.3, 0.7)
            amount_paid = amount * Decimal(str(percent_paid))
            amount_paid = amount_paid.quantize(Decimal('0.01'))
            paid_date = datetime.date.today() - datetime.timedelta(days=random.randint(1, 30))
        elif status_choice == 'paid':
            amount_paid = amount
            paid_date = datetime.date.today() - datetime.timedelta(days=random.randint(1, 30))
        
        fee = TuitionFee.objects.create(
            student=student,
            session=current_session,
            term=current_term,
            amount_due=amount,
            amount_paid=amount_paid,
            due_date=datetime.date.today() + datetime.timedelta(days=14),
            paid_date=paid_date,
            status=status_choice,
            created_by=admin_user,
            updated_by=admin_user
        )
        
        print(f"Created fee: {fee}")
        created_fees.append(fee)
    
    # Create payments for fees with payments
    print("\nCreating payments...")
    payment_methods = ['cash', 'bank', 'card', 'online']
    
    for fee in created_fees:
        if fee.status in ['partial', 'paid']:
            # Determine number of payments for this fee
            num_payments = 1 if fee.status == 'paid' else random.randint(1, 2)
            
            # For paid fees, make 1-2 payments adding up to the full amount
            # For partial fees, make 1-2 payments adding up to the partial amount
            remaining = fee.amount_paid
            
            for i in range(num_payments):
                is_last_payment = (i == num_payments - 1)
                
                if is_last_payment:
                    amount = remaining
                else:
                    # If not the last payment, pay a portion
                    max_for_this_payment = remaining * Decimal('0.8')
                    amount = max_for_this_payment * Decimal(str(random.uniform(0.4, 0.9)))
                    amount = amount.quantize(Decimal('0.01'))
                    remaining -= amount
                
                payment_date = fee.paid_date or datetime.date.today() - datetime.timedelta(days=random.randint(1, 30))
                payment_method = random.choice(payment_methods)
                
                payment = Payment.objects.create(
                    tuition_fee=fee,
                    amount=amount,
                    payment_date=payment_date,
                    method=payment_method,
                    receipt_number=f"REC-{random.randint(10000, 99999)}",
                    reference=f"REF-{random.randint(100000, 999999)}",
                    notes="Test payment data",
                    created_by=admin_user
                )
                
                print(f"Created payment: {payment}")
    
    # Create expenses
    print("\nCreating expenses...")
    expense_categories = ['supplies', 'maintenance', 'salary', 'utility', 'other']
    expense_descriptions = {
        'supplies': ['School supplies', 'Textbooks', 'Classroom materials', 'Office supplies'],
        'maintenance': ['Building repair', 'Equipment maintenance', 'Painting', 'Plumbing repairs'],
        'salary': ['Teacher salaries', 'Admin staff payment', 'Support staff wages'],
        'utility': ['Electricity bill', 'Water bill', 'Internet service', 'Telephone'],
        'other': ['Transportation', 'Events', 'Miscellaneous', 'Security']
    }
    
    # Create 15 expenses over the last 3 months
    for i in range(15):
        category = random.choice(expense_categories)
        description = random.choice(expense_descriptions[category])
        amount = Decimal(str(random.uniform(20000, 350000))).quantize(Decimal('0.01'))
        date = datetime.date.today() - datetime.timedelta(days=random.randint(1, 90))
        
        expense = Expense.objects.create(
            description=description,
            amount=amount,
            date=date,
            category=category,
            created_by=admin_user
        )
        
        print(f"Created expense: {expense}")
    
    # Create payroll data for the current month
    print("\nCreating payroll data...")
    current_month = datetime.date.today().strftime('%B')
    current_year = datetime.date.today().year
    
    # Get staff members
    staff_users = User.objects.filter(role='staff')
    if not staff_users:
        print("No staff users found, creating a sample staff member...")
        # Create a sample staff user
        staff_user = User.objects.create_user(
            username="staffmember1", 
            email="staff1@example.com", 
            password="password123",
            first_name="Staff",
            last_name="Member1",
            role="staff",
            is_staff=True
        )
        
        staff_profile = StaffProfile.objects.create(
            user=staff_user,
            staff_id="STF-2025-101",
            position="teacher",
            department="science"
        )
        staff_users = [staff_user]
    
    # Create payroll entries
    for staff_user in staff_users:
        try:
            staff_profile = staff_user.staff_profile
            
            # Check if payroll already exists
            existing_payroll = Payroll.objects.filter(
                staff=staff_profile,
                month=current_month,
                year=current_year
            ).first()
            
            if existing_payroll:
                print(f"Payroll already exists for {staff_profile}: {existing_payroll}")
                continue
            
            # Create random salary amount based on position
            if hasattr(staff_profile, 'position'):
                position = staff_profile.position
                if position == 'teacher':
                    amount = Decimal(str(random.uniform(120000, 180000)))
                elif position == 'admin':
                    amount = Decimal(str(random.uniform(140000, 200000)))
                elif position == 'accountant':
                    amount = Decimal(str(random.uniform(150000, 220000)))
                else:
                    amount = Decimal(str(random.uniform(100000, 150000)))
            else:
                amount = Decimal(str(random.uniform(100000, 180000)))
            
            amount = amount.quantize(Decimal('0.01'))
            
            # Randomly decide if paid
            is_paid = random.choice([True, False])
            paid_date = None
            if is_paid:
                paid_date = datetime.date.today() - datetime.timedelta(days=random.randint(1, 15))
            
            payroll = Payroll.objects.create(
                staff=staff_profile,
                month=current_month,
                year=current_year,
                amount=amount,
                paid=is_paid,
                paid_date=paid_date,
                created_by=admin_user,
                updated_by=admin_user
            )
            
            print(f"Created payroll: {payroll}")
            
        except Exception as e:
            print(f"Error creating payroll for {staff_user}: {e}")
    
    print("\nTest data creation complete!")

def validate_accounting_pages():
    """Test the accounting pages to ensure they display data correctly"""
    print_separator()
    print("VALIDATING ACCOUNTING PAGES")
    
    # Check if there's any data in the database
    from django.db.models import Count, Sum
    
    fee_count = TuitionFee.objects.count()
    payment_count = Payment.objects.count()
    expense_count = Expense.objects.count()
    
    print(f"Database status:")
    print(f" - Tuition Fees: {fee_count}")
    print(f" - Payments: {payment_count}")
    print(f" - Expenses: {expense_count}")
    
    if fee_count == 0 or payment_count == 0 or expense_count == 0:
        print("\nWarning: Some data is missing. The accounting pages may not display correctly.")
        print("Consider running the create_test_data() function to generate sample data.")
    else:
        print("\nDatabase contains accounting data. The pages should display correctly.")
    
    # Calculate some stats to compare with what's displayed in the UI
    total_due = TuitionFee.objects.aggregate(total=Sum('amount_due'))['total'] or 0
    total_paid = TuitionFee.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
    
    unpaid_count = TuitionFee.objects.filter(status='unpaid').count()
    partial_count = TuitionFee.objects.filter(status='partial').count()
    paid_count = TuitionFee.objects.filter(status='paid').count()
    
    print("\nFee Statistics (compare with UI):")
    print(f" - Total Amount Due: ₦{total_due:.2f}")
    print(f" - Total Amount Paid: ₦{total_paid:.2f}")
    print(f" - Collection Rate: {(total_paid/total_due)*100:.1f}% (if total_due > 0)")
    
    print(f"\nFee Status Breakdown:")
    print(f" - Unpaid: {unpaid_count}")
    print(f" - Partial: {partial_count}")
    print(f" - Paid: {paid_count}")
    
    # Get recent payments
    recent_payments = Payment.objects.all().order_by('-payment_date')[:5]
    print("\nRecent Payments (should appear in the UI):")
    for payment in recent_payments:
        print(f" - {payment.payment_date}: ₦{payment.amount:.2f} from {payment.tuition_fee.student.user.get_full_name()} ({payment.tuition_fee.student.admission_number})")
    
    # Get expense summary
    expense_total = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    print(f"\nExpense Total: ₦{expense_total:.2f}")
    
    # Instructions for manual verification
    print(f"\nManual Verification Steps:")
    print(f"1. Access the Fee Management page and verify:")
    print(f"   - The payment statistics match the numbers above")
    print(f"   - The recent payments table shows actual payment data")
    print(f"   - The progress bars reflect the correct collection rate")
    
    print(f"\n2. Access the Financial Reports page and verify:")
    print(f"   - The income statement reflects real data")
    print(f"   - The charts display accurate breakdowns")
    print(f"   - The monthly data chart shows historical trends")
    
    print_separator()

if __name__ == "__main__":
    print_separator()
    print("ACCOUNTING MODULE TEST SCRIPT")
    print_separator()
    
    # Validate current state of accounting pages
    validate_accounting_pages()
    
    # Create test data if needed
    create_option = input("Do you want to create test data for accounting module? (y/n): ")
    if create_option.lower() == 'y':
        create_test_data()
        # Re-run validation with new data
        validate_accounting_pages()
    
    print_separator()
    print("Testing complete. You can now access the accounting pages to verify they work correctly.")
    print("Accounting URLs:")
    print(" - /accounting/            # Home page")
    print(" - /accounting/fees/       # Fee Management")
    print(" - /accounting/reports/    # Financial Reports")
    print_separator()
