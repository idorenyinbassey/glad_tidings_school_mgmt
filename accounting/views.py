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
@accountant_required
def accounting_home(request):
    """
    Professional Finance Dashboard for Accountants with real-time financial metrics
    """
    from datetime import datetime, timedelta
    from django.db.models import Sum, Q, Count, Avg
    from decimal import Decimal
    import json
    
    # Check if this is an AJAX request for real-time data
    if request.GET.get('ajax'):
        ajax_type = request.GET.get('ajax')
        
        if ajax_type == 'revenue_data':
            # Return only monthly data for revenue chart
            today = timezone.now().date()
            current_month_start = today.replace(day=1)
            
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
            
            # Reverse to get chronological order
            monthly_data.reverse()
            
            return JsonResponse({
                'monthly_data': monthly_data,
                'status': 'success'
            })
        
        elif ajax_type == 'payment_methods':
            # Return payment method distribution data
            payment_methods = Payment.objects.values('method').annotate(
                total=Sum('amount'), count=Count('id')
            ).order_by('-total')
            
            payment_methods_data = []
            for method in payment_methods:
                payment_methods_data.append({
                    'payment_method': method['method'],
                    'total': float(method['total']),
                    'count': method['count']
                })
            
            return JsonResponse({
                'payment_methods': payment_methods_data,
                'status': 'success'
            })
        
        elif ajax_type == 'dashboard_metrics':
            # Return all dashboard metrics for complete refresh
            today = timezone.now().date()
            current_month_start = today.replace(day=1)
            
            # Revenue calculation
            total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            # Expenses calculation  
            total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            # Outstanding fees calculation
            outstanding_fees_data = TuitionFee.objects.aggregate(
                total_due=Sum('amount_due'),
                total_paid=Sum('amount_paid')
            )
            total_due = outstanding_fees_data['total_due'] or Decimal('0')
            total_paid = outstanding_fees_data['total_paid'] or Decimal('0')
            outstanding_fees = max(Decimal('0'), total_due - total_paid)
            
            # Collection rate
            collection_rate = (total_paid / total_due * 100) if total_due > 0 else 0
            
            # Overdue fees count
            overdue_fees = TuitionFee.objects.filter(
                status__in=['unpaid', 'partial'],
                due_date__lt=today
            ).count()
            
            return JsonResponse({
                'total_revenue': float(total_revenue),
                'total_expenses': float(total_expenses),
                'outstanding_fees': float(outstanding_fees),
                'collection_rate': float(collection_rate),
                'overdue_fees': overdue_fees,
                'net_income': float(total_revenue - total_expenses),
                'status': 'success'
            })
    
    # Regular dashboard view logic continues...
    
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
@accountant_required
def reports(request):
    """
    Financial reports with real database data
    """
    from .models import TuitionFee, Payment, Expense, Payroll
    from datetime import datetime, timedelta
    from django.db.models import Sum, Count, Avg
    import json
    
    # Get current date and calculate periods
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    current_year_start = today.replace(month=1, day=1)
    
    # Get filter parameters
    period_filter = request.GET.get('period', 'current_month')
    report_type = request.GET.get('type', 'income_statement')
    
    # Calculate date ranges based on filter
    if period_filter == 'current_month':
        start_date = current_month_start
        end_date = today
        period_name = today.strftime('%B %Y')
    elif period_filter == 'previous_month':
        start_date = (current_month_start - timedelta(days=1)).replace(day=1)
        end_date = current_month_start - timedelta(days=1)
        period_name = start_date.strftime('%B %Y')
    elif period_filter == 'current_year':
        start_date = current_year_start
        end_date = today
        period_name = f'Year {today.year}'
    elif period_filter == 'previous_year':
        start_date = current_year_start.replace(year=today.year - 1)
        end_date = current_year_start - timedelta(days=1)
        period_name = f'Year {today.year - 1}'
    else:  # default to current month
        start_date = current_month_start
        end_date = today
        period_name = today.strftime('%B %Y')
    
    # REVENUE CALCULATIONS (using Payment model - actual money received)
    total_revenue = Payment.objects.filter(
        payment_date__gte=start_date,
        payment_date__lte=end_date
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Revenue breakdown by payment method
    revenue_by_method = Payment.objects.filter(
        payment_date__gte=start_date,
        payment_date__lte=end_date
    ).values('method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # EXPENSE CALCULATIONS
    total_expenses = Expense.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Expense breakdown by category
    expense_categories = {}
    categories = ['supplies', 'maintenance', 'salary', 'utility', 'other']
    for category in categories:
        expense_categories[category] = Expense.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            category=category
        ).aggregate(total=Sum('amount'))['total'] or 0
    
    # PAYROLL CALCULATIONS
    if period_filter in ['current_month', 'previous_month']:
        # For monthly reports, filter by specific month
        target_month = start_date.strftime('%B')
        target_year = start_date.year
        payroll_data = Payroll.objects.filter(month=target_month, year=target_year)
    else:
        # For yearly reports, filter by year range
        payroll_data = Payroll.objects.filter(
            year__gte=start_date.year,
            year__lte=end_date.year
        )
    
    payroll_total = payroll_data.aggregate(total=Sum('amount'))['total'] or 0
    paid_payroll = payroll_data.filter(paid=True).aggregate(total=Sum('amount'))['total'] or 0
    unpaid_payroll = payroll_data.filter(paid=False).aggregate(total=Sum('amount'))['total'] or 0
    
    # FEE ANALYSIS (Outstanding vs Collected)
    total_fees_due = TuitionFee.objects.aggregate(total=Sum('amount_due'))['total'] or 0
    total_fees_paid = TuitionFee.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
    outstanding_fees = total_fees_due - total_fees_paid
    collection_rate = (total_fees_paid / total_fees_due * 100) if total_fees_due > 0 else 0
    
    # NET INCOME CALCULATION
    net_income = total_revenue - total_expenses
    
    # MONTHLY TREND DATA (last 6 months)
    monthly_data = []
    months = []
    revenue_trend = []
    expense_trend = []
    
    for i in range(5, -1, -1):
        month_date = (current_month_start - timedelta(days=32*i)).replace(day=1)
        month_end = (month_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_revenue = Payment.objects.filter(
            payment_date__gte=month_date,
            payment_date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        month_expenses = Expense.objects.filter(
            date__gte=month_date,
            date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        months.append(month_date.strftime('%b %Y'))
        revenue_trend.append(float(month_revenue))
        expense_trend.append(float(month_expenses))
        
        monthly_data.append({
            'month': month_date.strftime('%b %Y'),
            'revenue': float(month_revenue),
            'expenses': float(month_expenses),
            'net': float(month_revenue - month_expenses)
        })
    
    # RECENT ACTUAL REPORTS (from database or generate dynamically)
    recent_reports = []
    
    # Get recent high-value transactions for report history
    recent_payments = Payment.objects.order_by('-payment_date')[:5]
    recent_expenses = Expense.objects.order_by('-date')[:5]
    
    # Generate report entries based on actual data
    if recent_payments:
        recent_reports.append({
            'date': recent_payments[0].payment_date.strftime('%Y-%m-%d'),
            'name': 'Payment Collection Report',
            'period': recent_payments[0].payment_date.strftime('%B %Y'),
            'generated_by': request.user.get_full_name(),
            'format': 'PDF',
            'status': 'Generated'
        })
    
    if recent_expenses:
        recent_reports.append({
            'date': recent_expenses[0].date.strftime('%Y-%m-%d'),
            'name': 'Expense Analysis Report',
            'period': recent_expenses[0].date.strftime('%B %Y'),
            'generated_by': request.user.get_full_name(),
            'format': 'Excel',
            'status': 'Generated'
        })
    
    # Add some standard reports
    recent_reports.extend([
        {
            'date': today.strftime('%Y-%m-%d'),
            'name': 'Income Statement',
            'period': period_name,
            'generated_by': request.user.get_full_name(),
            'format': 'PDF',
            'status': 'Available'
        },
        {
            'date': today.strftime('%Y-%m-%d'),
            'name': 'Financial Summary',
            'period': period_name,
            'generated_by': request.user.get_full_name(),
            'format': 'Excel',
            'status': 'Available'
        }
    ])
    
    # STUDENT STATISTICS
    total_students = TuitionFee.objects.values('student').distinct().count()
    students_with_outstanding = TuitionFee.objects.filter(
        status__in=['unpaid', 'partial']
    ).values('student').distinct().count()
    
    context = {
        # Report metadata
        'report_type': report_type,
        'period_filter': period_filter,
        'period_name': period_name,
        'start_date': start_date,
        'end_date': end_date,
        'report_date': today.strftime('%B %d, %Y'),
        
        # Financial summary
        'total_revenue': total_revenue,
        'tuition_fees': total_revenue,  # For template compatibility
        'total_expenses': total_expenses,
        'net_income': net_income,
        'profit_margin': (net_income / total_revenue * 100) if total_revenue > 0 else 0,
        
        # Expense breakdown
        'expense_categories': expense_categories,
        
        # Payroll data
        'payroll_total': payroll_total,
        'paid_payroll': paid_payroll,
        'unpaid_payroll': unpaid_payroll,
        'payroll_completion': (paid_payroll / payroll_total * 100) if payroll_total > 0 else 0,
        
        # Fee analysis
        'total_fees_due': total_fees_due,
        'total_fees_paid': total_fees_paid,
        'outstanding_fees': outstanding_fees,
        'collection_rate': round(collection_rate, 1),
        
        # Revenue breakdown
        'revenue_by_method': json.dumps(list(revenue_by_method)),
        
        # Trends and charts
        'months': json.dumps(months),
        'revenue_trend': json.dumps(revenue_trend),
        'expense_trend': json.dumps(expense_trend),
        'monthly_data': json.dumps(monthly_data),
        
        # Recent data
        'recent_reports': recent_reports,
        'recent_payments': recent_payments,
        'recent_expenses': recent_expenses,
        
        # Statistics
        'total_students': total_students,
        'students_with_outstanding': students_with_outstanding,
        'payment_count': Payment.objects.filter(
            payment_date__gte=start_date,
            payment_date__lte=end_date
        ).count(),
        'expense_count': Expense.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).count(),
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
    from datetime import datetime
    
    payrolls = Payroll.objects.select_related('staff__user').order_by('-year', '-month')
    
    # Get current year and create year range
    current_year = datetime.now().year
    years = list(range(2020, current_year + 2))  # From 2020 to next year
    
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
    
    # List of months for filter dropdown
    months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    context = {
        'page_obj': page_obj,
        'years': years,
        'months': months,
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

@login_required
@staff_required
def generate_report_ajax(request):
    """AJAX endpoint for dynamic report generation"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    from .models import TuitionFee, Payment, Expense, Payroll
    from datetime import datetime, timedelta
    from django.db.models import Sum, Count
    import json
    
    # Get parameters
    report_type = request.POST.get('reportType', 'Income Statement')
    period = request.POST.get('datePeriod', 'Current Month')
    format_type = request.POST.get('format', 'PDF')
    start_date = request.POST.get('startDate')
    end_date = request.POST.get('endDate')
    
    # Calculate date ranges
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    current_year_start = today.replace(month=1, day=1)
    
    if period == 'Current Month':
        filter_start = current_month_start
        filter_end = today
        period_name = today.strftime('%B %Y')
    elif period == 'Previous Month':
        filter_start = (current_month_start - timedelta(days=1)).replace(day=1)
        filter_end = current_month_start - timedelta(days=1)
        period_name = filter_start.strftime('%B %Y')
    elif period == 'Current Term':
        # Assuming term is 3 months
        filter_start = current_month_start - timedelta(days=60)
        filter_end = today
        period_name = f'Current Term ({filter_start.strftime("%b")} - {today.strftime("%b %Y")})'
    elif period == 'Current Year':
        filter_start = current_year_start
        filter_end = today
        period_name = f'Year {today.year}'
    elif period == 'Previous Year':
        filter_start = current_year_start.replace(year=today.year - 1)
        filter_end = current_year_start - timedelta(days=1)
        period_name = f'Year {today.year - 1}'
    elif period == 'Custom Range' and start_date and end_date:
        filter_start = datetime.strptime(start_date, '%Y-%m-%d').date()
        filter_end = datetime.strptime(end_date, '%Y-%m-%d').date()
        period_name = f'{filter_start.strftime("%b %d")} - {filter_end.strftime("%b %d, %Y")}'
    else:
        filter_start = current_month_start
        filter_end = today
        period_name = today.strftime('%B %Y')
    
    try:
        # Calculate data based on report type
        if report_type == 'Income Statement':
            # Revenue calculations
            total_revenue = Payment.objects.filter(
                payment_date__gte=filter_start,
                payment_date__lte=filter_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Expense calculations
            total_expenses = Expense.objects.filter(
                date__gte=filter_start,
                date__lte=filter_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Expense breakdown
            expense_categories = {}
            categories = ['supplies', 'maintenance', 'salary', 'utility', 'other']
            for category in categories:
                expense_categories[category] = Expense.objects.filter(
                    date__gte=filter_start,
                    date__lte=filter_end,
                    category=category
                ).aggregate(total=Sum('amount'))['total'] or 0
            
            net_income = total_revenue - total_expenses
            profit_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0
            
            data = {
                'report_type': report_type,
                'period_name': period_name,
                'total_revenue': float(total_revenue),
                'tuition_fees': float(total_revenue),
                'total_expenses': float(total_expenses),
                'net_income': float(net_income),
                'profit_margin': round(profit_margin, 1),
                'expense_categories': {k: float(v) for k, v in expense_categories.items()},
                'report_date': today.strftime('%B %d, %Y')
            }
            
        elif report_type == 'Fee Collection Report':
            # Fee collection analysis
            total_fees_due = TuitionFee.objects.aggregate(total=Sum('amount_due'))['total'] or 0
            total_fees_paid = TuitionFee.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
            outstanding_fees = total_fees_due - total_fees_paid
            collection_rate = (total_fees_paid / total_fees_due * 100) if total_fees_due > 0 else 0
            
            # Recent payments in period
            recent_payments = Payment.objects.filter(
                payment_date__gte=filter_start,
                payment_date__lte=filter_end
            ).count()
            
            data = {
                'report_type': report_type,
                'period_name': period_name,
                'total_fees_due': float(total_fees_due),
                'total_fees_paid': float(total_fees_paid),
                'outstanding_fees': float(outstanding_fees),
                'collection_rate': round(collection_rate, 1),
                'recent_payments': recent_payments,
                'report_date': today.strftime('%B %d, %Y')
            }
            
        elif report_type == 'Expense Report':
            # Detailed expense analysis
            expenses = Expense.objects.filter(
                date__gte=filter_start,
                date__lte=filter_end
            )
            
            total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
            expense_count = expenses.count()
            
            # Category breakdown
            expense_by_category = expenses.values('category').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')
            
            data = {
                'report_type': report_type,
                'period_name': period_name,
                'total_expenses': float(total_expenses),
                'expense_count': expense_count,
                'expense_by_category': list(expense_by_category),
                'report_date': today.strftime('%B %d, %Y')
            }
            
        else:
            # Default to basic summary
            data = {
                'report_type': report_type,
                'period_name': period_name,
                'message': f'{report_type} report generated successfully',
                'report_date': today.strftime('%B %d, %Y')
            }
        
        return JsonResponse({
            'success': True,
            'data': data,
            'message': f'{report_type} for {period_name} generated successfully in {format_type} format'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error generating report: {str(e)}'
        }, status=500)

@login_required
@staff_required
def generate_payroll_ajax(request):
    """AJAX endpoint for payroll generation"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    from .models import Payroll
    from staff.models import Staff
    from datetime import datetime
    
    try:
        month = request.POST.get('month')
        year = int(request.POST.get('year', datetime.now().year))
        
        if not month:
            return JsonResponse({'success': False, 'error': 'Month is required'})
        
        # Check if payroll already exists for this period
        existing_payroll = Payroll.objects.filter(month=month, year=year)
        if existing_payroll.exists():
            return JsonResponse({
                'success': False, 
                'error': f'Payroll for {month} {year} already exists. Use the edit function to modify existing payroll.'
            })
        
        # Get all active staff members
        staff_members = Staff.objects.filter(user__is_active=True)
        
        if not staff_members.exists():
            return JsonResponse({'success': False, 'error': 'No active staff members found'})
        
        # Generate payroll entries
        created_count = 0
        for staff in staff_members:
            # Use basic salary or default amount
            base_salary = getattr(staff, 'basic_salary', 50000)  # Default basic salary
            
            payroll, created = Payroll.objects.get_or_create(
                staff=staff,
                month=month,
                year=year,
                defaults={
                    'amount': base_salary,
                    'basic_salary': base_salary,
                    'allowances': 0,
                    'deductions': 0,
                    'paid': False
                }
            )
            
            if created:
                created_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Payroll generated successfully for {month} {year}. Created {created_count} payroll entries.',
            'created_count': created_count,
            'total_staff': staff_members.count()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error generating payroll: {str(e)}'
        }, status=500)

@login_required
@staff_required
def dashboard_stats_ajax(request):
    """AJAX endpoint for live dashboard statistics"""
    from .models import TuitionFee, Payment, Expense, Payroll
    from django.db.models import Sum, Count
    from datetime import datetime, timedelta
    
    try:
        today = timezone.now().date()
        current_month_start = today.replace(day=1)
        current_year_start = today.replace(month=1, day=1)
        
        # Revenue this month
        monthly_revenue = Payment.objects.filter(
            payment_date__gte=current_month_start,
            payment_date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Expenses this month
        monthly_expenses = Expense.objects.filter(
            date__gte=current_month_start,
            date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Outstanding fees
        outstanding_fees = TuitionFee.objects.filter(
            status__in=['unpaid', 'partial']
        ).aggregate(total=Sum('amount_due'))['total'] or 0
        
        # Recent transactions count
        recent_payments = Payment.objects.filter(
            payment_date__gte=today - timedelta(days=7)
        ).count()
        
        # Monthly trend data (last 6 months)
        monthly_trends = []
        for i in range(5, -1, -1):
            month_date = (current_month_start - timedelta(days=32*i)).replace(day=1)
            month_end = (month_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_revenue = Payment.objects.filter(
                payment_date__gte=month_date,
                payment_date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            month_expenses = Expense.objects.filter(
                date__gte=month_date,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_trends.append({
                'month': month_date.strftime('%b'),
                'revenue': float(month_revenue),
                'expenses': float(month_expenses)
            })
        
        return JsonResponse({
            'success': True,
            'stats': {
                'monthly_revenue': float(monthly_revenue),
                'monthly_expenses': float(monthly_expenses),
                'outstanding_fees': float(outstanding_fees),
                'recent_payments': recent_payments,
                'monthly_trends': monthly_trends,
                'last_updated': today.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error fetching dashboard stats: {str(e)}'
        }, status=500)
