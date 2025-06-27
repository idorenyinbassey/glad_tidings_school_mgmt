
import os
import sys
import django
import time

# Add project directory to path so Django can find settings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "glad_school_portal.settings")
django.setup()

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.contrib.auth import get_user_model
from users.models import CustomUser
from accounting.models import TuitionFee, Payment, Expense
from students.models import StudentProfile

def analyze_query_performance():
    print("Analyzing database query performance...")
    
    # Test 1: Retrieving all users
    with CaptureQueriesContext(connection) as ctx:
        start_time = time.time()
        users = list(CustomUser.objects.all())
        elapsed = time.time() - start_time
        print(f"Retrieved {len(users)} users in {elapsed:.4f} seconds")
        print(f"Number of queries: {len(ctx.captured_queries)}")
    
    # Test 2: Retrieving students with profiles
    with CaptureQueriesContext(connection) as ctx:
        start_time = time.time()
        students = list(CustomUser.objects.filter(role="student").select_related("student_profile"))
        elapsed = time.time() - start_time
        print(f"Retrieved {len(students)} students with profiles in {elapsed:.4f} seconds")
        print(f"Number of queries: {len(ctx.captured_queries)}")
    
    # Test 3: Retrieving tuition fees with payments
    with CaptureQueriesContext(connection) as ctx:
        start_time = time.time()
        fees = list(TuitionFee.objects.all().select_related("student").prefetch_related("payments"))
        elapsed = time.time() - start_time
        print(f"Retrieved {len(fees)} tuition fees with payments in {elapsed:.4f} seconds")
        print(f"Number of queries: {len(ctx.captured_queries)}")
    
    # Test 4: Complex query for financial reporting
    with CaptureQueriesContext(connection) as ctx:
        start_time = time.time()
        total_fees = TuitionFee.objects.all().count()
        total_payments = Payment.objects.all().count()
        total_expenses = Expense.objects.all().count()
        fees_sum = TuitionFee.objects.all().values_list("amount_due", flat=True)
        payments_sum = Payment.objects.all().values_list("amount", flat=True)
        expenses_sum = Expense.objects.all().values_list("amount", flat=True)
        elapsed = time.time() - start_time
        print(f"Financial summary generated in {elapsed:.4f} seconds")
        print(f"Number of queries: {len(ctx.captured_queries)}")
    
if __name__ == "__main__":
    analyze_query_performance()

