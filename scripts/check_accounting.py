"""
Script to check accounting data in the database
"""

import os
import django
import sys

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glad_school_portal.settings')
django.setup()

from accounting.models import TuitionFee, Payment, Expense
from staff.models import StaffProfile
from users.models import CustomUser

def check_tuition_fees():
    """Check tuition fees in the system"""
    fees = TuitionFee.objects.all()
    print(f"\nTotal tuition fees: {fees.count()}")
    
    # Status breakdown
    print("\nTuition fee status breakdown:")
    unpaid = fees.filter(status='unpaid').count()
    partial = fees.filter(status='partial').count()
    paid = fees.filter(status='paid').count()
    print(f"- Unpaid: {unpaid}")
    print(f"- Partial: {partial}")
    print(f"- Paid: {paid}")
    
    # Recent fees
    print("\nMost recent tuition fees:")
    for fee in fees.order_by('-created_at')[:5]:
        print(f"- {fee.student} - ₦{fee.amount_due} - {fee.status}")

def check_payments():
    """Check payments in the system"""
    payments = Payment.objects.all()
    print(f"\nTotal payments: {payments.count()}")
    
    # Method breakdown
    print("\nPayment method breakdown:")
    for method in ['cash', 'bank', 'card', 'online']:
        count = payments.filter(method=method).count()
        print(f"- {method.title()}: {count}")
    
    # Recent payments
    print("\nMost recent payments:")
    for payment in payments.order_by('-payment_date')[:5]:
        print(f"- {payment.tuition_fee.student} - ₦{payment.amount} - {payment.method} - {payment.payment_date}")
        
    # Total amount paid
    total_paid = sum(payment.amount for payment in payments)
    print(f"\nTotal amount paid: ₦{total_paid:,}")

def check_expenses():
    """Check expenses in the system"""
    expenses = Expense.objects.all()
    print(f"\nTotal expenses: {expenses.count()}")
    
    # Category breakdown
    print("\nExpense category breakdown:")
    for category in ['supplies', 'maintenance', 'salary', 'utility', 'other']:
        category_expenses = expenses.filter(category=category)
        count = category_expenses.count()
        amount = sum(expense.amount for expense in category_expenses)
        print(f"- {category.title()}: {count} items, total: ₦{amount:,}")
    
    # Recent expenses
    print("\nMost recent expenses:")
    for expense in expenses.order_by('-date')[:5]:
        print(f"- {expense.description} - ₦{expense.amount} - {expense.category}")
    
    # Total expenses
    total_expenses = sum(expense.amount for expense in expenses)
    print(f"\nTotal expenses: ₦{total_expenses:,}")

def check_accountant():
    """Check accountant user details"""
    try:
        accountant = CustomUser.objects.get(username='accountant')
        print("\nAccountant User:")
        print(f"- Username: {accountant.username}")
        print(f"- Name: {accountant.get_full_name()}")
        print(f"- Role: {accountant.role}")
        
        profile = StaffProfile.objects.get(user=accountant)
        print("\nAccountant Profile:")
        print(f"- Staff ID: {profile.staff_id}")
        print(f"- Position: {profile.position}")
        print(f"- Department: {profile.department}")
    except CustomUser.DoesNotExist:
        print("\nAccountant user not found!")
    except StaffProfile.DoesNotExist:
        print("\nAccountant profile not found!")

if __name__ == "__main__":
    print("ACCOUNTING SYSTEM REPORT")
    print("=" * 50)
    
    check_accountant()
    check_tuition_fees()
    check_payments()
    check_expenses()
