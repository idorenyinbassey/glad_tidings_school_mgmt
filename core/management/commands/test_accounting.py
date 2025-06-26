"""
Django management command to test the accounting pages functionality.
"""
from django.core.management.base import BaseCommand
import datetime
import random
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from students.models import StudentProfile
from accounting.models import TuitionFee, Payment, Expense, Payroll
from staff.models import StaffProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Test and validate the accounting pages and create test data if needed'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-data',
            action='store_true',
            help='Create test data for the accounting module',
        )
        
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(self.style.SUCCESS('ACCOUNTING MODULE TEST'))
        self.stdout.write(self.style.SUCCESS('='*80))
        
        # Validate current state of accounting pages
        self.validate_accounting_pages()
        
        # Create test data if needed
        if options['create_data']:
            self.create_test_data()
            # Re-run validation with new data
            self.validate_accounting_pages()
        
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(self.style.SUCCESS('Testing complete. You can now access the accounting pages to verify they work correctly.'))
        self.stdout.write(self.style.SUCCESS('Accounting URLs:'))
        self.stdout.write(self.style.SUCCESS(' - /accounting/            # Home page'))
        self.stdout.write(self.style.SUCCESS(' - /accounting/fees/       # Fee Management'))
        self.stdout.write(self.style.SUCCESS(' - /accounting/reports/    # Financial Reports'))
        self.stdout.write(self.style.SUCCESS('='*80))
    
    def create_test_data(self):
        """Create test data for accounting module"""
        self.stdout.write(self.style.SUCCESS("Starting test data creation for accounting module..."))
        
        # Create sample students if they don't exist
        students_data = []
        classes = ['Nursery 1', 'Primary 3', 'Primary 6', 'JSS 1', 'JSS 3', 'SS 2']
        
        for i in range(1, 6):
            username = f"student{i}"
            try:
                user = User.objects.get(username=username)
                student = user.student_profile
                self.stdout.write(f"Found existing student: {student}")
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
                self.stdout.write(f"Created student: {student}")
                
            students_data.append(student)
        
        # Create tuition fees
        self.stdout.write(self.style.SUCCESS("\nCreating tuition fees..."))
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
                self.stdout.write(f"Fee already exists for {student}: {existing_fee}")
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
            
            self.stdout.write(f"Created fee: {fee}")
            created_fees.append(fee)
        
        # Create payments for fees that need them
        self.stdout.write(self.style.SUCCESS("\nCreating payments..."))
        payment_methods = ['cash', 'bank', 'card', 'online']
        
        for fee in created_fees:
            if fee.status in ['partial', 'paid']:
                # Reset the fee's amount_paid to 0 first
                fee.amount_paid = Decimal('0.00')
                fee.save(update_fields=['amount_paid'])
                
                # Determine number of payments for this fee
                if fee.status == 'paid':
                    target_amount = fee.amount_due
                    num_payments = random.randint(1, 2)  # 1 or 2 payments for full amount
                else:  # partial
                    target_amount = fee.amount_due * Decimal(str(random.uniform(0.3, 0.7)))
                    target_amount = target_amount.quantize(Decimal('0.01'))
                    num_payments = random.randint(1, 2)  # 1 or 2 payments for partial amount
                
                # Split the total payment into multiple payments if needed
                remaining = target_amount
                
                for i in range(num_payments):
                    is_last_payment = (i == num_payments - 1)
                    
                    if is_last_payment:
                        amount = remaining
                    else:
                        # If not the last payment, pay a portion
                        amount = remaining * Decimal(str(random.uniform(0.3, 0.7)))
                        amount = amount.quantize(Decimal('0.01'))
                        remaining -= amount
                    
                    payment_date = datetime.date.today() - datetime.timedelta(days=random.randint(1, 30))
                    payment_method = random.choice(payment_methods)
                    
                    try:
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
                        self.stdout.write(f"Created payment: {payment}")
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f"Error creating payment: {e}"))
                
                # Update the fee status manually to match the expected status
                fee = TuitionFee.objects.get(pk=fee.pk)  # Refresh from DB
                fee.status = 'paid' if fee.amount_paid >= fee.amount_due else 'partial'
                if fee.status == 'paid':
                    fee.paid_date = payment_date
                fee.save(update_fields=['status', 'paid_date'])
        
        # Create expenses
        self.stdout.write(self.style.SUCCESS("\nCreating expenses..."))
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
            
            self.stdout.write(f"Created expense: {expense}")
        
        self.stdout.write(self.style.SUCCESS("\nTest data creation complete!"))
    
    def validate_accounting_pages(self):
        """Test the accounting pages to ensure they display data correctly"""
        self.stdout.write(self.style.SUCCESS("\nVALIDATING ACCOUNTING PAGES"))
        
        # Check if there's any data in the database
        fee_count = TuitionFee.objects.count()
        payment_count = Payment.objects.count()
        expense_count = Expense.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f"Database status:"))
        self.stdout.write(f" - Tuition Fees: {fee_count}")
        self.stdout.write(f" - Payments: {payment_count}")
        self.stdout.write(f" - Expenses: {expense_count}")
        
        if fee_count == 0 or payment_count == 0 or expense_count == 0:
            self.stdout.write(self.style.WARNING("\nWarning: Some data is missing. The accounting pages may not display correctly."))
            self.stdout.write(self.style.WARNING("Consider using --create-data option to generate sample data."))
        else:
            self.stdout.write(self.style.SUCCESS("\nDatabase contains accounting data. The pages should display correctly."))
        
        # Calculate some stats to compare with what's displayed in the UI
        total_due = TuitionFee.objects.aggregate(total=Sum('amount_due'))['total'] or 0
        total_paid = TuitionFee.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
        
        unpaid_count = TuitionFee.objects.filter(status='unpaid').count()
        partial_count = TuitionFee.objects.filter(status='partial').count()
        paid_count = TuitionFee.objects.filter(status='paid').count()
        
        self.stdout.write(self.style.SUCCESS("\nFee Statistics (compare with UI):"))
        self.stdout.write(f" - Total Amount Due: ₦{total_due:.2f}")
        self.stdout.write(f" - Total Amount Paid: ₦{total_paid:.2f}")
        if total_due > 0:
            self.stdout.write(f" - Collection Rate: {(total_paid/total_due)*100:.1f}%")
        
        self.stdout.write(self.style.SUCCESS(f"\nFee Status Breakdown:"))
        self.stdout.write(f" - Unpaid: {unpaid_count}")
        self.stdout.write(f" - Partial: {partial_count}")
        self.stdout.write(f" - Paid: {paid_count}")
        
        # Get recent payments
        recent_payments = Payment.objects.all().order_by('-payment_date')[:5]
        self.stdout.write(self.style.SUCCESS("\nRecent Payments (should appear in the UI):"))
        for payment in recent_payments:
            self.stdout.write(f" - {payment.payment_date}: ₦{payment.amount:.2f} from {payment.tuition_fee.student.user.get_full_name()} ({payment.tuition_fee.student.admission_number})")
        
        # Get expense summary
        expense_total = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        self.stdout.write(self.style.SUCCESS(f"\nExpense Total: ₦{expense_total:.2f}"))
        
        # Instructions for manual verification
        self.stdout.write(self.style.SUCCESS(f"\nManual Verification Steps:"))
        self.stdout.write(f"1. Access the Fee Management page and verify:")
        self.stdout.write(f"   - The payment statistics match the numbers above")
        self.stdout.write(f"   - The recent payments table shows actual payment data")
        self.stdout.write(f"   - The progress bars reflect the correct collection rate")
        
        self.stdout.write(f"\n2. Access the Financial Reports page and verify:")
        self.stdout.write(f"   - The income statement reflects real data")
        self.stdout.write(f"   - The charts display accurate breakdowns")
        self.stdout.write(f"   - The monthly data chart shows historical trends")
