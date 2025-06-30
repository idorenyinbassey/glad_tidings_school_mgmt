from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
from core.decorators import staff_required, accountant_required
from .models import TuitionFee, Payment, Expense, Payroll
from .forms import TuitionFeeForm, PaymentForm, ExpenseForm, PayrollForm
from students.models import StudentProfile

@login_required
@staff_required
def accounting_home(request):
    """
    Professional Finance Dashboard for Accountants with real-time financial metrics
    """
    from datetime import datetime, timedelta
    from django.db.models import Sum, Q, Count, Avg
    from decimal import Decimal
    import json
    
    # Date ranges for analysis
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    current_year_start = today.replace(month=1, day=1)
    
    # Financial Metrics
    total_revenue = Payment.objects.filter(
        payment_date__year=today.year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    total_expenses = Expense.objects.filter(
        date__year=today.year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Calculate outstanding fees (amount_due - amount_paid for unpaid/partial fees)
    from django.db.models import F
    outstanding_fees_data = TuitionFee.objects.filter(
        status__in=['unpaid', 'partial']
    ).aggregate(
        total_due=Sum('amount_due'),
        total_paid=Sum('amount_paid')
    )
    
    total_due = outstanding_fees_data['total_due'] or Decimal('0')
    total_paid = outstanding_fees_data['total_paid'] or Decimal('0')
    outstanding_fees = max(Decimal('0'), total_due - total_paid)
    
    # Collection Rate Calculation
    total_fees_due = TuitionFee.objects.aggregate(total=Sum('amount_due'))['total'] or Decimal('0')
    total_collected = Payment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    collection_rate = (total_collected / total_fees_due * 100) if total_fees_due > 0 else 0
    
    # Monthly Comparisons
    current_month_revenue = Payment.objects.filter(
        payment_date__gte=current_month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    last_month_revenue = Payment.objects.filter(
        payment_date__gte=last_month_start,
        payment_date__lt=current_month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    revenue_growth = ((current_month_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else 0
    
    # Payment method breakdown
    payment_methods = Payment.objects.values('method').annotate(
        total=Sum('amount'), count=Count('id')
    ).order_by('-total')
    
    # Recent payments (last 5)
    recent_payments = Payment.objects.select_related('tuition_fee__student__user').order_by('-payment_date')[:5]
    
    # Pending actions
    overdue_fees = TuitionFee.objects.filter(
        status__in=['unpaid', 'partial'],
        due_date__lt=today
    ).count()
    
    unverified_payments = 0  # No status field in Payment model
    
    # Financial trends for charts (last 6 months)
    monthly_data = []
    for i in range(6):
        month_start = (current_month_start - timedelta(days=32*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_revenue = Payment.objects.filter(
            payment_date__gte=month_start,
            payment_date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        month_expenses = Expense.objects.filter(
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(month_revenue),
            'expenses': float(month_expenses)
        })
    
    monthly_data.reverse()  # Show chronologically
    
    # Quick stats for today, week, month
    today_payments = Payment.objects.filter(
        payment_date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    week_start = today - timedelta(days=today.weekday())
    week_payments = Payment.objects.filter(
        payment_date__gte=week_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    month_payments = Payment.objects.filter(
        payment_date__gte=current_month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Recent fee transactions for table
    recent_fees = TuitionFee.objects.select_related('student__user').order_by('-created_at')[:10]
    
    # Convert payment methods to JSON-safe format
    payment_methods_data = []
    for method in payment_methods:
        payment_methods_data.append({
            'payment_method': method['method'] or 'Unknown',
            'total': float(method['total'] or 0),
            'count': method['count']
        })
    
    context = {
        # Financial Metrics
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'outstanding_fees': outstanding_fees,
        'collection_rate': round(collection_rate, 1),
        'net_income': total_revenue - total_expenses,
        
        # Growth & Trends
        'revenue_growth': round(revenue_growth, 1),
        'monthly_data': json.dumps(monthly_data),
        'payment_methods': payment_methods_data,
        
        # Quick Stats
        'today_payments': today_payments,
        'week_payments': week_payments,
        'month_payments': month_payments,
        
        # Recent Activity
        'recent_payments': recent_payments,
        'recent_fees': recent_fees,
        
        # Pending Actions
        'overdue_fees': overdue_fees,
        'unverified_payments': unverified_payments,
        
        # Additional metrics
        'total_students_with_fees': TuitionFee.objects.values('student').distinct().count(),
        'average_fee_amount': TuitionFee.objects.aggregate(avg=Avg('amount_due'))['avg'] or Decimal('0'),
    }
    
    return render(request, 'accounting/accounting_home.html', context)

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

# =================== TUITION FEE MANAGEMENT ===================

@login_required
@staff_required
def fee_list(request):
    """List all tuition fees with filtering and pagination"""
    fees = TuitionFee.objects.select_related('student__user').order_by('-created_at')
    
    # Search and filtering
    search = request.GET.get('search')
    status_filter = request.GET.get('status')
    session_filter = request.GET.get('session')
    term_filter = request.GET.get('term')
    
    if search:
        fees = fees.filter(
            Q(student__user__first_name__icontains=search) |
            Q(student__user__last_name__icontains=search) |
            Q(student__admission_number__icontains=search)
        )
    
    if status_filter:
        fees = fees.filter(status=status_filter)
    
    if session_filter:
        fees = fees.filter(session=session_filter)
        
    if term_filter:
        fees = fees.filter(term=term_filter)
    
    # Pagination
    paginator = Paginator(fees, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique sessions and terms for filters
    sessions = TuitionFee.objects.values_list('session', flat=True).distinct()
    terms = TuitionFee.objects.values_list('term', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'session_filter': session_filter,
        'term_filter': term_filter,
        'sessions': sessions,
        'terms': terms,
        'fee_stats': TuitionFee.get_fee_statistics(),
    }
    
    return render(request, 'accounting/fee_list.html', context)

@login_required
@staff_required
def fee_create(request):
    """Create a new tuition fee"""
    if request.method == 'POST':
        form = TuitionFeeForm(request.POST)
        if form.is_valid():
            fee = form.save(commit=False)
            fee.created_by = request.user
            fee.save()
            messages.success(request, f'Tuition fee created for {fee.student}')
            return redirect('accounting:fee_detail', pk=fee.pk)
    else:
        form = TuitionFeeForm()
    
    return render(request, 'accounting/fee_form.html', {
        'form': form,
        'title': 'Create Tuition Fee'
    })

@login_required
@staff_required
def fee_detail(request, pk):
    """View detailed tuition fee information"""
    fee = get_object_or_404(TuitionFee, pk=pk)
    payments = fee.payments.all().order_by('-payment_date')
    
    context = {
        'fee': fee,
        'payments': payments,
        'payment_form': PaymentForm() if request.user.has_perm('accounting.add_payment') else None,
    }
    
    return render(request, 'accounting/fee_detail.html', context)

@login_required
@staff_required
def fee_edit(request, pk):
    """Edit existing tuition fee"""
    fee = get_object_or_404(TuitionFee, pk=pk)
    
    if request.method == 'POST':
        form = TuitionFeeForm(request.POST, instance=fee)
        if form.is_valid():
            fee = form.save(commit=False)
            fee.updated_by = request.user
            fee.save()
            messages.success(request, f'Tuition fee updated for {fee.student}')
            return redirect('accounting:fee_detail', pk=fee.pk)
    else:
        form = TuitionFeeForm(instance=fee)
    
    return render(request, 'accounting/fee_form.html', {
        'form': form,
        'fee': fee,
        'title': 'Edit Tuition Fee'
    })

# =================== PAYMENT MANAGEMENT ===================

@login_required
@staff_required
def payment_create(request, fee_pk=None):
    """Create a new payment"""
    fee = None
    if fee_pk:
        fee = get_object_or_404(TuitionFee, pk=fee_pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            try:
                payment.save()
                messages.success(request, f'Payment of ₦{payment.amount:,.2f} recorded successfully')
                return redirect('accounting:fee_detail', pk=payment.tuition_fee.pk)
            except ValueError as e:
                messages.error(request, str(e))
    else:
        initial = {'tuition_fee': fee} if fee else {}
        form = PaymentForm(initial=initial)
    
    return render(request, 'accounting/payment_form.html', {
        'form': form,
        'fee': fee,
        'title': 'Record Payment'
    })

@login_required
@staff_required
def payment_list(request):
    """List all payments with filtering"""
    payments = Payment.objects.select_related('tuition_fee__student__user').order_by('-payment_date')
    
    # Filtering
    method_filter = request.GET.get('method')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')
    
    if method_filter:
        payments = payments.filter(method=method_filter)
    
    if date_from:
        payments = payments.filter(payment_date__gte=date_from)
    
    if date_to:
        payments = payments.filter(payment_date__lte=date_to)
    
    if search:
        payments = payments.filter(
            Q(tuition_fee__student__user__first_name__icontains=search) |
            Q(tuition_fee__student__user__last_name__icontains=search) |
            Q(receipt_number__icontains=search) |
            Q(reference__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(payments, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Summary statistics
    total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
    payment_methods = Payment.objects.values('method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'page_obj': page_obj,
        'total_amount': total_amount,
        'payment_methods': payment_methods,
        'method_filter': method_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search': search,
    }
    
    return render(request, 'accounting/payment_list.html', context)

# =================== EXPENSE MANAGEMENT ===================

@login_required
@staff_required
def expense_list(request):
    """List all expenses with filtering"""
    expenses = Expense.objects.order_by('-date')
    
    # Filtering
    category_filter = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')
    
    if category_filter:
        expenses = expenses.filter(category=category_filter)
    
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    
    if date_to:
        expenses = expenses.filter(date__lte=date_to)
    
    if search:
        expenses = expenses.filter(description__icontains=search)
    
    # Pagination
    paginator = Paginator(expenses, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Summary
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    category_totals = expenses.values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'page_obj': page_obj,
        'total_expenses': total_expenses,
        'category_totals': category_totals,
        'category_filter': category_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search': search,
        'categories': Expense.EXPENSE_CATEGORIES,
    }
    
    return render(request, 'accounting/expense_list.html', context)

@login_required
@staff_required
def expense_create(request):
    """Create a new expense"""
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()
            messages.success(request, f'Expense of ₦{expense.amount:,.2f} recorded')
            return redirect('accounting:expense_list')
    else:
        form = ExpenseForm()
    
    return render(request, 'accounting/expense_form.html', {
        'form': form,
        'title': 'Record Expense'
    })

# =================== PAYROLL MANAGEMENT ===================

@login_required
@staff_required
def payroll_list(request):
    """List payroll records with filtering"""
    payrolls = Payroll.objects.select_related('staff__user').order_by('-year', '-month')
    
    # Filtering
    year_filter = request.GET.get('year')
    month_filter = request.GET.get('month')
    paid_filter = request.GET.get('paid')
    
    if year_filter:
        payrolls = payrolls.filter(year=year_filter)
    
    if month_filter:
        payrolls = payrolls.filter(month=month_filter)
    
    if paid_filter:
        paid_status = paid_filter.lower() == 'true'
        payrolls = payrolls.filter(paid=paid_status)
    
    # Pagination
    paginator = Paginator(payrolls, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Summary
    total_payroll = payrolls.aggregate(total=Sum('amount'))['total'] or 0
    paid_payroll = payrolls.filter(paid=True).aggregate(total=Sum('amount'))['total'] or 0
    unpaid_payroll = payrolls.filter(paid=False).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'page_obj': page_obj,
        'total_payroll': total_payroll,
        'paid_payroll': paid_payroll,
        'unpaid_payroll': unpaid_payroll,
        'year_filter': year_filter,
        'month_filter': month_filter,
        'paid_filter': paid_filter,
    }
    
    return render(request, 'accounting/payroll_list.html', context)

# =================== AJAX ENDPOINTS ===================

@login_required
@staff_required
def student_search_ajax(request):
    """AJAX endpoint for student search"""
    query = request.GET.get('q', '')
    students = StudentProfile.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query) |
        Q(admission_number__icontains=query)
    ).select_related('user')[:10]
    
    results = [{
        'id': student.id,
        'text': f"{student.user.get_full_name()} ({student.admission_number})"
    } for student in students]
    
    return JsonResponse({'results': results})

@login_required
@staff_required
def fee_statistics_ajax(request):
    """AJAX endpoint for fee statistics"""
    stats = TuitionFee.get_fee_statistics()
    return JsonResponse(stats)
