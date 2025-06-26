from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.utils import timezone
from core.decorators import staff_required, accountant_required

@login_required
@staff_required
def accounting_home(request):
    print(f"User accessing accounting: {request.user.username}, role: {request.user.role}")
    return render(request, 'accounting/accounting_home.html')

@login_required
@staff_required
def fees(request):
    # Fetch tuition fees data from the database
    from .models import TuitionFee, Payment
    
    # Get recent tuition fees
    recent_fees = TuitionFee.objects.all().order_by('-created_at')[:10]
    
    # Get payment summary
    payments = Payment.objects.all()[:10]  # Already ordered by -payment_date, -created_at
    
    # Get fee statistics
    fee_stats = TuitionFee.get_fee_statistics()
    
    context = {
        'fees': recent_fees,
        'payments': payments,
        **fee_stats,  # Unpacks all statistics
    }
    
    return render(request, 'accounting/fees.html', context)

@login_required
@staff_required
def reports(request):
    # Import necessary models
    from .models import TuitionFee, Payment, Expense, Payroll
    from datetime import datetime, timedelta
    
    # Get current date and calculate start of month and previous month
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    last_month_start = (first_day_of_month - timedelta(days=1)).replace(day=1)
    last_month_end = first_day_of_month - timedelta(days=1)
    
    # Revenue data for current month
    tuition_fees_current = TuitionFee.objects.filter(
        paid_date__gte=first_day_of_month,
        paid_date__lte=today
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # Get expenses for current month by category
    expenses_current = Expense.objects.filter(
        date__gte=first_day_of_month,
        date__lte=today
    )
    
    total_expenses_current = expenses_current.aggregate(total=Sum('amount'))['total'] or 0
    
    expense_categories = {
        'supplies': expenses_current.filter(category='supplies').aggregate(total=Sum('amount'))['total'] or 0,
        'maintenance': expenses_current.filter(category='maintenance').aggregate(total=Sum('amount'))['total'] or 0,
        'salary': expenses_current.filter(category='salary').aggregate(total=Sum('amount'))['total'] or 0,
        'utility': expenses_current.filter(category='utility').aggregate(total=Sum('amount'))['total'] or 0,
        'other': expenses_current.filter(category='other').aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Calculate payroll data
    current_month_name = today.strftime('%B')
    current_year = today.year
    
    payroll_data = Payroll.objects.filter(
        month=current_month_name,
        year=current_year
    )
    
    payroll_total = payroll_data.aggregate(total=Sum('amount'))['total'] or 0
    paid_payroll = payroll_data.filter(paid=True).aggregate(total=Sum('amount'))['total'] or 0
    unpaid_payroll = payroll_data.filter(paid=False).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get payment method distribution
    payment_methods = Payment.objects.filter(
        payment_date__gte=first_day_of_month,
        payment_date__lte=today
    ).values('method').annotate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    # Create monthly data for charts (last 6 months)
    months = []
    income_data = []
    expense_data = []
    
    for i in range(5, -1, -1):
        # Calculate the month
        month_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        month_date = month_date.replace(month=(today.month - i) % 12 or 12)
        if month_date.month > today.month:
            month_date = month_date.replace(year=today.year - 1)
        
        month_name = month_date.strftime('%B')
        next_month = month_date.replace(month=month_date.month % 12 + 1)
        if next_month.month == 1:
            next_month = next_month.replace(year=month_date.year + 1)
        
        # Get income for this month
        month_income = TuitionFee.objects.filter(
            paid_date__gte=month_date,
            paid_date__lt=next_month
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        # Get expenses for this month
        month_expenses = Expense.objects.filter(
            date__gte=month_date,
            date__lt=next_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        months.append(month_name)
        income_data.append(float(month_income))
        expense_data.append(float(month_expenses))
    
    # Generate some sample recent reports (this would be real data in production)
    recent_reports = [
        {
            'date': (today - timedelta(days=15)).strftime('%Y-%m-%d'),
            'name': 'Income Statement',
            'period': (today - timedelta(days=45)).strftime('%B %Y'),
            'generated_by': request.user.get_full_name(),
            'format': 'PDF'
        },
        {
            'date': (today - timedelta(days=30)).strftime('%Y-%m-%d'),
            'name': 'Fee Collection Report',
            'period': f"Term 2, {today.year}",
            'generated_by': request.user.get_full_name(),
            'format': 'Excel'
        },
        {
            'date': (today - timedelta(days=45)).strftime('%Y-%m-%d'),
            'name': 'Balance Sheet',
            'period': f"As of {(today - timedelta(days=45)).strftime('%B %d, %Y')}",
            'generated_by': request.user.get_full_name(),
            'format': 'PDF'
        }
    ]
    
    context = {
        # Financial summary
        'tuition_fees': tuition_fees_current,
        'total_expenses': total_expenses_current,
        'net_income': tuition_fees_current - total_expenses_current,
        
        # Expense categories
        'expense_categories': expense_categories,
        
        # Payroll data
        'payroll_total': payroll_total,
        'paid_payroll': paid_payroll,
        'unpaid_payroll': unpaid_payroll,
        
        # Payment methods
        'payment_methods': list(payment_methods),
        
        # Chart data
        'months': months,
        'income_data': income_data,
        'expense_data': expense_data,
        
        # Report generation date
        'report_date': today.strftime('%B %d, %Y'),
        
        # Sample recent reports
        'recent_reports': recent_reports,
    }
    
    return render(request, 'accounting/reports.html', context)
