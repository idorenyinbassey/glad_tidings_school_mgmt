from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from decimal import Decimal
from .models import TuitionFee, Payment, Expense, Payroll, FinancialReport
from .forms import TuitionFeeForm, PaymentForm, ExpenseForm
from core.decorators import staff_required, accountant_required
import json


@login_required
def accounting_home(request):
    """Accounting module dashboard with financial overview"""
    context = {}
    
    # Initialize default values
    monthly_trends = []
    fee_categories = []
    expense_categories = []
    payment_methods = []
    monthly_fees = 0
    monthly_payments = 0
    monthly_expenses = 0
    outstanding_fees = 0
    recent_payments = []
    recent_expenses = []
    fee_stats = []
    
    try:
        # Current financial statistics
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        # Total fees for current month
        monthly_fees = TuitionFee.objects.filter(
            created_at__month=current_month,
            created_at__year=current_year
        ).aggregate(total=Sum('amount_due'))['total'] or 0
        
        # Total payments for current month  
        monthly_payments = Payment.objects.filter(
            payment_date__month=current_month,
            payment_date__year=current_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Total expenses for current month
        monthly_expenses = Expense.objects.filter(
            date__month=current_month,
            date__year=current_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Outstanding fees
        outstanding_fees = TuitionFee.objects.filter(
            status='unpaid'
        ).aggregate(total=Sum('amount_due'))['total'] or 0
        
        # Recent transactions
        recent_payments = Payment.objects.select_related('tuition_fee').order_by('-payment_date')[:5]
        recent_expenses = Expense.objects.order_by('-date')[:5]
        
        # Fee statistics by status
        fee_stats = TuitionFee.objects.values('status').annotate(
            count=Count('id'),
            total=Sum('amount_due')
        )
        
        # Monthly trends (last 6 months)
        monthly_trends = []
        for i in range(6):
            month_date = timezone.now().replace(day=1) - timezone.timedelta(days=30*i)
            month_payments = Payment.objects.filter(
                payment_date__month=month_date.month,
                payment_date__year=month_date.year
            ).aggregate(total=Sum('amount'))['total'] or 0

            month_expenses = Expense.objects.filter(
                date__month=month_date.month,
                date__year=month_date.year
            ).aggregate(total=Sum('amount'))['total'] or 0

            # Use keys expected by the frontend JS: 'revenue' and 'expenses'
            monthly_trends.append({
                'month': month_date.strftime('%B %Y'),
                'revenue': float(month_payments),
                'expenses': float(month_expenses),
                'net': float(month_payments - month_expenses)
            })
        
        monthly_trends.reverse()  # Show oldest to newest
        
        # Top fee categories (using session and term as categories)
        fee_categories = TuitionFee.objects.values('session', 'term').annotate(
            count=Count('id'),
            total=Sum('amount_due')
        ).order_by('-total')[:5]
        
        # Top expense categories
        expense_categories = Expense.objects.values('category').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-total')[:5]
        
        # Payment methods analysis
        payment_methods = Payment.objects.values('method').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-total')

        # Build a frontend-friendly list of {label, value} for charts
        payment_methods_serializable = []
        for pm in payment_methods:
            label = pm.get('method') or 'Unknown'
            total = pm.get('total') or 0
            try:
                value = float(total)
            except Exception:
                value = total
            payment_methods_serializable.append({'label': label, 'value': value})
        
        # Additional calculations for template compatibility
        total_revenue = monthly_payments
        total_expenses = monthly_expenses
        net_income = monthly_payments - monthly_expenses
        
        # Calculate overdue fees (unpaid fees past due date)
        overdue_fees = TuitionFee.objects.filter(
            status='unpaid',
            due_date__lt=timezone.now().date()
        ).count()
        
        # Calculate collection rate (percentage of paid vs total fees)
        total_fees_amount = TuitionFee.objects.aggregate(total=Sum('amount_due'))['total'] or 1
        paid_fees_amount = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
        collection_rate = round((paid_fees_amount / total_fees_amount) * 100, 1) if total_fees_amount > 0 else 0
        
        # Payment summaries for dashboard
        today_payments = Payment.objects.filter(payment_date=timezone.now().date()).aggregate(total=Sum('amount'))['total'] or 0
        week_start = timezone.now().date() - timezone.timedelta(days=7)
        week_payments = Payment.objects.filter(payment_date__gte=week_start).aggregate(total=Sum('amount'))['total'] or 0
        month_payments = monthly_payments
        
        # Recent payments count
        recent_payments_count = Payment.objects.filter(
            payment_date__gte=timezone.now().date() - timezone.timedelta(days=7)
        ).count()

        # Unverified payments count (use actual DB flag)
        try:
            unverified_payments = Payment.objects.filter(verified=False).count()
        except Exception:
            # Fallback for older DBs or before migration
            unverified_payments = recent_payments_count

        # Show most recent fees, no filters
        recent_fees = TuitionFee.objects.select_related('student', 'student__user').order_by('-created_at')[:5]
        context.update({
            'monthly_fees': monthly_fees,
            'monthly_payments': monthly_payments,
            'monthly_expenses': monthly_expenses,
            'outstanding_fees': outstanding_fees,
            'recent_payments': recent_payments,
            'recent_expenses': recent_expenses,
            'recent_fees': recent_fees,
            'fee_stats': fee_stats,
            'monthly_trends': monthly_trends,
            'fee_categories': fee_categories,
            'expense_categories': expense_categories,
            'payment_methods': payment_methods,
            'net_income': net_income,
            'current_month': timezone.now().strftime('%B %Y'),

            # Template-specific variables
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'overdue_fees': overdue_fees,
            'collection_rate': collection_rate,
            'today_payments': today_payments,
            'week_payments': week_payments,
            'month_payments': month_payments,
            'recent_payments_count': recent_payments_count,
            'unverified_payments': unverified_payments,
            'revenue_growth': 0,  # TODO: Calculate actual growth
        })
        
        # Additional context for charts and graphs
        # Convert querysets and decimal values to JSON-serializable format
        def make_json_serializable(queryset):
            """Convert queryset with Decimal fields to JSON-serializable format"""
            result = []
            for item in queryset:
                json_item = {}
                for key, value in item.items():
                    if hasattr(value, '__float__'):  # Convert Decimal to float
                        json_item[key] = float(value)
                    else:
                        json_item[key] = value
                result.append(json_item)
            return result
        
        context.update({
            'monthly_trends_json': json.dumps(monthly_trends),  # Already converted to float in loop
            'payment_methods_json': json.dumps(payment_methods_serializable),
            'fee_categories_json': json.dumps(make_json_serializable(fee_categories)),
            'expense_categories_json': json.dumps(make_json_serializable(expense_categories))
        })
        
    except Exception as e:
        messages.error(request, f'Error loading financial data: {str(e)}')
        
    # Quick access links for common tasks
    context['quick_links'] = [
        {
            'title': 'Record Payment',
            'url': 'accounting:payment_create',
            'icon': 'fas fa-plus-circle',
            'description': 'Record a new fee payment'
        },
        {
            'title': 'Create Fee',
            'url': 'accounting:fee_create', 
            'icon': 'fas fa-file-invoice-dollar',
            'description': 'Create a new tuition fee'
        },
        {
            'title': 'Add Expense',
            'url': 'accounting:expense_create',
            'icon': 'fas fa-minus-circle', 
            'description': 'Record a new expense'
        },
        {
            'title': 'Generate Report',
            'url': 'accounting:reports',
            'icon': 'fas fa-chart-bar',
            'description': 'Generate financial reports'
        }
    ]
    
    # Dashboard alerts and notifications
    alerts = []
    
    # Check for overdue fees
    overdue_count = TuitionFee.objects.filter(
        status='unpaid',
        due_date__lt=timezone.now().date()
    ).count()
    
    if overdue_count > 0:
        alerts.append({
            'type': 'warning',
            'message': f'{overdue_count} overdue fee(s) require attention',
            'url': 'accounting:fee_list'
        })
    
    # Check for high expenses this month
    if monthly_expenses > monthly_payments:
        alerts.append({
            'type': 'danger',
            'message': 'Monthly expenses exceed payments',
            'url': 'accounting:expense_list'
        })
    
    # Check for pending payroll
    pending_payroll = Payroll.objects.filter(paid=False).count()
    if pending_payroll > 0:
        alerts.append({
            'type': 'info',
            'message': f'{pending_payroll} pending payroll item(s)',
            'url': 'accounting:payroll_list'
        })
    
    context['alerts'] = alerts
    context['total_alerts'] = len(alerts)
    
    return render(request, 'accounting/accounting_home.html', context)


@login_required 
@staff_required
def fees(request):
    """Fees management page"""
    context = {}
    
    try:
        # Get fee statistics from actual data
        current_year = timezone.now().year
        current_session = f"{current_year}/{current_year + 1}"
        
        # Get class-wise fee summary from actual TuitionFee records
        from django.db.models import Avg, Count
        
        # Get fee data grouped by student class and session
        class_fees = TuitionFee.objects.filter(
            session=current_session
        ).select_related('student').values(
            'student__current_class'
        ).annotate(
            avg_amount=Avg('amount_due'),
            count=Count('id')
        ).order_by('student__current_class')
        
        # Fee structure for display (based on actual data or defaults)
        fee_structure = []
        
        # If we have real data, use it
        if class_fees:
            for class_fee in class_fees:
                class_name = class_fee['student__current_class'] or 'Unknown'
                avg_amount = class_fee['avg_amount'] or 0
                fee_structure.append({
                    'class_level': class_name,
                    'tuition_fee': avg_amount,
                    'books': avg_amount * Decimal('0.2'),  # 20% of tuition
                    'uniform': avg_amount * Decimal('0.15'),  # 15% of tuition  
                    'development': avg_amount * Decimal('0.1'),  # 10% of tuition
                    'total': avg_amount * Decimal('1.45')  # Total with extras
                })
        else:
            # Default fee structure if no data exists
            default_classes = [
                ('Pre-Nursery', 150000),
                ('Nursery 1', 180000),
                ('Nursery 2', 200000),
                ('Primary 1', 220000),
                ('Primary 2', 240000),
                ('Primary 3', 250000),
                ('Primary 4', 270000),
                ('Primary 5', 280000),
                ('Primary 6', 300000),
                ('JSS 1', 320000),
                ('JSS 2', 340000),
                ('JSS 3', 360000),
                ('SSS 1', 380000),
                ('SSS 2', 400000),
                ('SSS 3', 420000),
            ]
            
            for class_name, tuition in default_classes:
                tuition = Decimal(str(tuition))
                fee_structure.append({
                    'class_level': class_name,
                    'tuition_fee': tuition,
                    'books': tuition * Decimal('0.2'),
                    'uniform': tuition * Decimal('0.15'),
                    'development': tuition * Decimal('0.1'),
                    'total': tuition * Decimal('1.45')
                })
        
        context['fee_structure'] = fee_structure
        context['current_session'] = current_session

        # Add recent payments for the payments table
        from .models import Payment
        payments = Payment.objects.select_related('tuition_fee', 'tuition_fee__student', 'tuition_fee__student__user').order_by('-payment_date')[:10]
        context['payments'] = payments
    
    except Exception as e:
        messages.error(request, f'Error loading fee structure: {str(e)}')
        context['fee_structure'] = []
        context['current_session'] = f"{timezone.now().year}/{timezone.now().year + 1}"
        context['payments'] = []
    
    return render(request, 'accounting/fees.html', context)


@login_required
@staff_required  
def reports(request):
    """Reports page with dynamic report generation"""
    context = {}
    
    try:
        # Available report types
        report_types = [
            {
                'value': 'income_statement',
                'label': 'Income Statement',
                'description': 'Revenue vs expenses summary'
            },
            {
                'value': 'balance_sheet',
                'label': 'Balance Sheet', 
                'description': 'Assets, liabilities, and equity'
            },
            {
                'value': 'cash_flow',
                'label': 'Cash Flow Statement',
                'description': 'Cash inflows and outflows'
            },
            {
                'value': 'fee_collection',
                'label': 'Fee Collection Report',
                'description': 'Student fee payments and outstanding amounts'
            },
            {
                'value': 'expense_report',
                'label': 'Expense Report',
                'description': 'Detailed expense breakdown by category'
            }
        ]
        
        # Available time periods
        time_periods = [
            {
                'value': 'current_month',
                'label': 'Current Month',
                'description': timezone.now().strftime('%B %Y')
            },
            {
                'value': 'last_month',
                'label': 'Last Month',
                'description': (timezone.now().replace(day=1) - timezone.timedelta(days=1)).strftime('%B %Y')
            },
            {
                'value': 'current_quarter',
                'label': 'Current Quarter',
                'description': f'Q{((timezone.now().month-1)//3)+1} {timezone.now().year}'
            },
            {
                'value': 'last_quarter',
                'label': 'Last Quarter', 
                'description': 'Previous quarter'
            },
            {
                'value': 'current_year',
                'label': 'Current Year',
                'description': str(timezone.now().year)
            },
            {
                'value': 'last_year',
                'label': 'Last Year',
                'description': str(timezone.now().year - 1)
            },
            {
                'value': 'custom',
                'label': 'Custom Range',
                'description': 'Select specific dates'
            }
        ]
        
        # Export formats
        export_formats = [
            {'value': 'PDF', 'label': 'PDF', 'icon': 'fas fa-file-pdf'},
            {'value': 'EXCEL', 'label': 'Excel', 'icon': 'fas fa-file-excel'},
            {'value': 'CSV', 'label': 'CSV', 'icon': 'fas fa-file-csv'}
        ]
        
        # Recent reports
        recent_reports = FinancialReport.objects.filter(
            generated_by=request.user,
            is_available=True
        ).order_by('-generated_at')[:10]
        
        # Report generation statistics
        total_reports = FinancialReport.objects.filter(
            generated_by=request.user
        ).count()
        
        reports_this_month = FinancialReport.objects.filter(
            generated_by=request.user,
            generated_at__month=timezone.now().month,
            generated_at__year=timezone.now().year
        ).count()
        
        context.update({
            'report_types': report_types,
            'time_periods': time_periods,
            'export_formats': export_formats,
            'recent_reports': recent_reports,
            'total_reports': total_reports,
            'reports_this_month': reports_this_month,
            'current_date': timezone.now().date(),
            'max_date': timezone.now().date(),
            'min_date': timezone.now().date().replace(year=timezone.now().year - 5)
        })
        
    except Exception as e:
        messages.error(request, f'Error loading reports page: {str(e)}')
    
    return render(request, 'accounting/reports_dynamic.html', context)


# Fee Management Views
@login_required
@staff_required
def fee_list(request):
    """List all tuition fees with search and filtering"""
    fees = TuitionFee.objects.select_related('student').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        fees = fees.filter(
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(student__admission_number__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        fees = fees.filter(status=status_filter)
    
    # Filter by session
    session_filter = request.GET.get('session')
    if session_filter:
        fees = fees.filter(session=session_filter)
    
    # Date range filtering
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        fees = fees.filter(created_at__date__gte=date_from)
    if date_to:
        fees = fees.filter(created_at__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(fees, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Summary statistics
    total_fees = fees.aggregate(total=Sum('amount_due'))['total'] or 0
    pending_fees = fees.filter(status='pending').aggregate(total=Sum('amount_due'))['total'] or 0
    paid_fees = fees.filter(status='paid').aggregate(total=Sum('amount_due'))['total'] or 0
    unpaid_fees = fees.filter(status='unpaid').aggregate(total=Sum('amount_due'))['total'] or 0
    
    # Calculate collection stats
    total_paid_amount = Payment.objects.filter(tuition_fee__in=fees).aggregate(total=Sum('amount'))['total'] or 0
    outstanding_amount = total_fees - total_paid_amount
    collection_percentage = (total_paid_amount / total_fees * 100) if total_fees > 0 else 0
    
    # Get available sessions for filtering
    available_sessions = TuitionFee.objects.values_list('session', flat=True).distinct().order_by('session')
    available_terms = TuitionFee.objects.values_list('term', flat=True).distinct().order_by('term')
    
    # Create fee_stats object for template compatibility
    fee_stats = {
        'total_due': total_fees,
        'total_paid': total_paid_amount,
        'outstanding': outstanding_amount,
        'collection_percentage': collection_percentage
    }
    
    # Prepare context and render the fee list template
    context = {
        'fees': fees,
        'page_obj': page_obj,
        'paginator': paginator,
        'fee_stats': fee_stats,
        'available_sessions': available_sessions,
        'available_terms': available_terms,
        'filters': {
            'status': status_filter,
            'session': session_filter,
            'q': search_query,
            'date_from': date_from,
            'date_to': date_to,
        }
    }

    return render(request, 'accounting/fee_list.html', context)


@login_required
@staff_required
def fee_detail(request, pk):
    """View fee details and associated payments"""
    fee = get_object_or_404(TuitionFee, pk=pk)
    payments = fee.payments.all().order_by('-payment_date')
    
    context = {
        'fee': fee,
        'payments': payments,
        'remaining_amount': fee.amount_outstanding,
        'payment_percentage': fee.payment_percentage
    }
    
    return render(request, 'accounting/fee_detail.html', context)


@login_required
@staff_required
def fee_edit(request, pk):
    """Edit an existing fee"""
    fee = get_object_or_404(TuitionFee, pk=pk)
    
    if request.method == 'POST':
        form = TuitionFeeForm(request.POST, instance=fee)
        if form.is_valid():
            fee = form.save(commit=False)
            fee.updated_by = request.user
            fee.save()
            messages.success(request, 'Fee updated successfully')
            return redirect('accounting:fee_detail', pk=fee.pk)
    else:
        form = TuitionFeeForm(instance=fee)
    
    return render(request, 'accounting/fee_form.html', {
        'form': form,
        'fee': fee,
        'title': 'Edit Fee'
    })


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
            messages.success(request, f'Fee created successfully for {fee.student}')
            return redirect('accounting:fee_detail', pk=fee.pk)
    else:
        form = TuitionFeeForm()
    
    return render(request, 'accounting/fee_form.html', {
        'form': form,
        'title': 'Create New Fee'
    })


# Payment Management Views
@login_required
@staff_required
def payment_create(request, fee_pk=None):
    """Create a new payment, optionally for a specific fee"""
    initial_data = {}
    fee = None
    
    if fee_pk:
        fee = get_object_or_404(TuitionFee, pk=fee_pk)
        initial_data['fee'] = fee
        initial_data['amount'] = fee.amount_outstanding
    else:
        initial_data['fee'] = None
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.recorded_by = request.user
            payment.save()
            messages.success(request, f'Payment of {payment.amount} recorded successfully')
            
            if fee:
                return redirect('accounting:fee_detail', pk=fee.pk)
            return redirect('accounting:payment_list')
    else:
        form = PaymentForm(initial=initial_data)
    
    return render(request, 'accounting/payment_form.html', {
        'form': form,
        'fee': fee,
        'title': 'Record Payment'
    })


@login_required
@staff_required
def payment_list(request):
    """List all payments with search and filtering"""
    payments = Payment.objects.select_related('tuition_fee', 'created_by').order_by('-payment_date')
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        payments = payments.filter(
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(student__admission_number__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Filter by payment method
    method_filter = request.GET.get('method')
    if method_filter:
        payments = payments.filter(method=method_filter)
    
    # Date range filtering
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        payments = payments.filter(date__gte=date_from)
    if date_to:
        payments = payments.filter(date__lte=date_to)
    
    # Amount range filtering
    amount_min = request.GET.get('amount_min')
    amount_max = request.GET.get('amount_max')
    if amount_min:
        payments = payments.filter(amount__gte=amount_min)
    if amount_max:
        payments = payments.filter(amount__lte=amount_max)
    
    # Pagination
    paginator = Paginator(payments, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Summary statistics
    total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
    avg_payment = payments.aggregate(avg=Sum('amount'))['avg'] or 0
    payment_count = payments.count()
    
    # Payment methods breakdown
    payment_methods = payments.values('method').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-total')
    
    context = {
        'page_obj': page_obj,
        'total_payments': total_payments,
        'avg_payment': avg_payment,
        'payment_count': payment_count,
        'payment_methods': payment_methods,
        'search_query': search_query,
        'method_filter': method_filter,
        'date_from': date_from,
        'date_to': date_to,
        'amount_min': amount_min,
        'amount_max': amount_max,
        'available_methods': Payment.PAYMENT_METHODS
    }
    
    return render(request, 'accounting/payment_list.html', context)


@login_required
@staff_required
def verify_payment(request, pk):
    """AJAX endpoint to mark a payment as verified"""
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse, HttpResponseBadRequest
    from django.utils import timezone

    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')

    payment = get_object_or_404(Payment, pk=pk)
    if payment.verified:
        return JsonResponse({'success': True, 'already_verified': True, 'payment_id': payment.pk})

    payment.verified = True
    payment.verified_by = request.user
    payment.verified_at = timezone.now()
    payment.save(update_fields=['verified', 'verified_by', 'verified_at'])

    return JsonResponse({'success': True, 'payment_id': payment.pk})


# Expense Management Views  
@login_required
@staff_required
def expense_list(request):
    """List all expenses with search and filtering"""
    expenses = Expense.objects.select_related('created_by').order_by('-date')
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        expenses = expenses.filter(
            Q(description__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        expenses = expenses.filter(category=category_filter)
    
    # Date range filtering
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)
    
    # Amount range filtering
    amount_min = request.GET.get('amount_min')
    amount_max = request.GET.get('amount_max')
    if amount_min:
        expenses = expenses.filter(amount__gte=amount_min)
    if amount_max:
        expenses = expenses.filter(amount__lte=amount_max)
    
    # Pagination
    paginator = Paginator(expenses, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Summary statistics
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    avg_expense = expenses.aggregate(avg=Sum('amount'))['avg'] or 0
    expense_count = expenses.count()
    
    # Category breakdown
    expense_categories = expenses.values('category').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-total')
    
    context = {
        'page_obj': page_obj,
        'total_expenses': total_expenses,
        'avg_expense': avg_expense,
        'expense_count': expense_count,
        'expense_categories': expense_categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'date_from': date_from,
        'date_to': date_to,
        'amount_min': amount_min,
        'amount_max': amount_max,
        'available_categories': Expense.EXPENSE_CATEGORIES
    }
    
    return render(request, 'accounting/expense_list.html', context)


@login_required
@staff_required
def expense_create(request):
    """Create a new expense"""
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()
            messages.success(request, f'Expense of {expense.amount} recorded successfully')
            return redirect('accounting:expense_list')
    else:
        form = ExpenseForm()
    
    return render(request, 'accounting/expense_form.html', {
        'form': form,
        'title': 'Record Expense'
    })


# Payroll Management Views
@login_required
@staff_required
def payroll_list(request):
    """List all payroll records"""
    payroll_records = Payroll.objects.select_related('staff', 'created_by').order_by('-year', '-month')
    
    # Filter by staff
    staff_filter = request.GET.get('staff')
    if staff_filter:
        payroll_records = payroll_records.filter(staff_id=staff_filter)
    
    # Filter by month/year
    month_filter = request.GET.get('month')
    year_filter = request.GET.get('year')
    if month_filter:
        payroll_records = payroll_records.filter(month=month_filter)
    if year_filter:
        payroll_records = payroll_records.filter(year=year_filter)
    
    # Filter by payment status
    paid_filter = request.GET.get('paid')
    if paid_filter is not None:
        payroll_records = payroll_records.filter(paid=paid_filter == 'true')
    
    # Pagination
    paginator = Paginator(payroll_records, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Summary statistics
    total_amount = payroll_records.aggregate(total=Sum('amount'))['total'] or 0
    pending_payments = payroll_records.filter(paid=False).aggregate(total=Sum('amount'))['total'] or 0
    paid_amount = payroll_records.filter(paid=True).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'page_obj': page_obj,
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'pending_payments': pending_payments,
        'staff_filter': staff_filter,
        'month_filter': month_filter,
        'year_filter': year_filter,
        'paid_filter': paid_filter,
        'current_year': timezone.now().year,
        'years_range': range(timezone.now().year - 2, timezone.now().year + 1),
        'months_range': range(1, 13)
    }
    
    return render(request, 'accounting/payroll_list.html', context)


@login_required
@staff_required
def generate_payroll_ajax(request):
    """AJAX endpoint to generate payroll for a specific month/year"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        
        if not (1 <= month <= 12):
            return JsonResponse({'error': 'Invalid month'}, status=400)
        
        if year < 2020 or year > timezone.now().year + 1:
            return JsonResponse({'error': 'Invalid year'}, status=400)
        
        # Check if payroll already exists for this month/year
        existing_payroll = Payroll.objects.filter(month=month, year=year)
        if existing_payroll.exists():
            return JsonResponse({
                'error': f'Payroll for {month}/{year} already exists',
                'existing_count': existing_payroll.count()
            }, status=400)
        
        # Get all staff members (using User.is_active instead of StaffProfile.is_active)
        from staff.models import StaffProfile
        
        staff_members = StaffProfile.objects.filter(user__is_active=True)
        if not staff_members.exists():
            return JsonResponse({'error': 'No active staff members found'}, status=400)
        
        payroll_records = []
        for staff in staff_members:
            # Calculate salary based on position
            position_salaries = {
                'teacher': 120000.00,
                'admin': 150000.00,
                'accountant': 180000.00,
                'it_support': 100000.00,
                'other': 80000.00,
            }
            
            salary = position_salaries.get(staff.position, 100000.00)
            
            # Create payroll record 
            payroll = Payroll.objects.create(
                staff=staff,
                month=month,
                year=year,
                amount=salary,
                paid=False,
                created_by=request.user
            )
            payroll_records.append(payroll)
        
        return JsonResponse({
            'success': True,
            'message': f'Payroll generated for {month}/{year}',
            'count': len(payroll_records),
            'total_amount': sum(p.amount for p in payroll_records)
        })
        
    except ValueError:
        return JsonResponse({'error': 'Invalid month or year format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Failed to generate payroll: {str(e)}'}, status=500)


# AJAX Views
@login_required
def student_search_ajax(request):
    """AJAX endpoint for student search"""
    query = request.GET.get('q', '')
    students = []
    
    if len(query) >= 2:
        from students.models import Student
        student_list = Student.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(admission_number__icontains=query)
        )[:10]
        
        students = [{
            'id': student.id,
            'name': student.get_full_name(),
            'admission_number': student.admission_number,
            'class_name': str(student.current_class) if student.current_class else 'No Class'
        } for student in student_list]
    
    return JsonResponse({'students': students})


@login_required
def fee_statistics_ajax(request):
    """AJAX endpoint for fee statistics"""
    stats = TuitionFee.get_fee_statistics()
    return JsonResponse(stats)


@login_required
@staff_required
def generate_report_ajax(request):
    """AJAX endpoint to generate reports dynamically"""
    from .models import FinancialReport
    from .report_utils import get_report_data
    from .file_generators import generate_report_file
    from datetime import datetime, timedelta
    from django.http import JsonResponse
    from decimal import Decimal
    import uuid
    import logging
    import json

    logger = logging.getLogger(__name__)
    
    class DecimalEncoder(json.JSONEncoder):
        """Custom JSON encoder for Decimal objects"""
        def default(self, obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return super(DecimalEncoder, self).default(obj)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Get parameters
        report_type = request.POST.get('report_type', 'income_statement')
        period = request.POST.get('time_period', 'current_month')
        format_type = request.POST.get('format', 'PDF')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        # Validate report type
        valid_report_types = ['income_statement', 'balance_sheet', 'cash_flow', 'fee_collection', 'expense_report']
        if report_type not in valid_report_types:
            report_type = 'income_statement'

        # Calculate date range based on period
        now = timezone.now()
        if period == 'current_month':
            start_date = now.replace(day=1).date()
            end_date = now.date()
            period_name = now.strftime('%B %Y')
        elif period == 'last_month':
            last_month = now.replace(day=1) - timedelta(days=1)
            start_date = last_month.replace(day=1).date()
            end_date = last_month.date()
            period_name = last_month.strftime('%B %Y')
        elif period == 'current_quarter':
            quarter = ((now.month - 1) // 3) + 1
            start_date = now.replace(month=((quarter-1)*3)+1, day=1).date()
            end_date = now.date()
            period_name = f'Q{quarter} {now.year}'
        elif period == 'current_year':
            start_date = now.replace(month=1, day=1).date()
            end_date = now.date()
            period_name = str(now.year)
        elif period == 'custom' and start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            period_name = f'{start_date.strftime("%b %d, %Y")} - {end_date.strftime("%b %d, %Y")}'
        else:
            return JsonResponse({'error': 'Invalid date period'}, status=400)

        # Generate report data
        report_data = get_report_data(report_type, start_date, end_date, period_name)
        
        # Convert any Decimal objects to float for JSON serialization
        def convert_decimals(obj):
            """Recursively convert Decimal objects to float"""
            from datetime import date, datetime
            if isinstance(obj, dict):
                return {key: convert_decimals(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimals(item) for item in obj]
            elif isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, (date, datetime)):
                return obj.isoformat() if hasattr(obj, 'isoformat') else str(obj)
            else:
                return obj
        
        # Convert report data for JSON serialization BEFORE saving to database
        serializable_data = convert_decimals(report_data)
        
        # Debug logging to see what we're trying to serialize
        logger.info(f"Original report data type: {type(report_data)}")
        logger.info(f"Serializable data type: {type(serializable_data)}")
        
        # Test JSON serialization
        try:
            import json
            test_json = json.dumps(serializable_data)
            logger.info("JSON serialization test passed")
        except Exception as json_error:
            logger.error(f"JSON serialization test failed: {json_error}")
            logger.error(f"Problematic data: {serializable_data}")
            # Try to find the problematic object
            def find_problematic_object(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        find_problematic_object(value, f"{path}.{key}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        find_problematic_object(item, f"{path}[{i}]")
                else:
                    try:
                        json.dumps(obj)
                    except:
                        logger.error(f"Problematic object at {path}: {type(obj)} - {obj}")
            find_problematic_object(serializable_data)
            raise json_error
        
        # Create FinancialReport record with converted data
        financial_report = FinancialReport.objects.create(
            report_type=report_type,
            format=format_type,
            period_start=start_date,
            period_end=end_date,
            period_name=period_name,
            report_data=serializable_data,  # Use converted data here
            generated_by=request.user
        )

        # Generate file if requested
        if format_type in ['PDF', 'EXCEL', 'CSV']:
            try:
                file_path = generate_report_file(financial_report, format_type)
                financial_report.file = file_path
                financial_report.save()
            except Exception as file_error:
                logger.error(f"Error generating file: {file_error}")
                # Continue without file - data is still available

        return JsonResponse({
            'success': True,
            'report_id': str(financial_report.id),
            'message': f'{report_type.replace("_", " ").title()} generated successfully',
            'report_data': serializable_data,
            'download_url': f'/accounting/reports/download/{financial_report.id}/' if financial_report.file else None
        })

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()  # Print full traceback for debugging
        
        return JsonResponse({
            'success': False,
            'error': str(e),
            'debug_info': f'Report type: {report_type}, Period: {period}'  # Debug info
        }, status=500)


@login_required
@staff_required
def export_report_ajax(request):
    """AJAX endpoint to export existing reports in different formats"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        report_id = request.POST.get('reportId')
        export_format = request.POST.get('format', 'PDF')
        
        # Get the existing report
        report = get_object_or_404(FinancialReport, id=report_id, generated_by=request.user)
        
        # Generate file in requested format
        from .file_generators import ReportFileGenerator
        from django.core.files.base import ContentFile
        import json
        
        # Parse report data if it's JSON string
        if isinstance(report.report_data, str):
            report_data = json.loads(report.report_data)
        else:
            report_data = report.report_data
        
        # Generate file content
        generator = ReportFileGenerator(report_data, report.report_type, export_format)
        file_content = generator.generate()
        
        # Create file name
        file_extension = export_format.lower()
        if file_extension == 'excel':
            file_extension = 'xlsx'
        
        filename = f"{report.report_type}_{report.period_name.replace(' ', '_')}_{report.id}.{file_extension}"
        
        # Save file to report
        report.file.save(filename, ContentFile(file_content.getvalue()), save=False)
        report.format = export_format
        report.save()

        return JsonResponse({
            'success': True,
            'download_url': f'/accounting/reports/download/{report.id}/',
            'message': f'Report exported as {export_format} successfully'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@staff_required
def download_report(request, report_id):
    """Download a generated financial report"""
    try:
        report = get_object_or_404(
            FinancialReport, 
            id=report_id, 
            generated_by=request.user,
            is_available=True
        )
        
        if not report.file:
            messages.error(request, 'Report file not found')
            return redirect('accounting:reports')
        
        # Increment download count
        report.increment_download_count()
        
        # Serve file
        response = HttpResponse(
            report.file.read(),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{report.file.name}"'
        return response
        
    except Exception as e:
        messages.error(request, f'Error downloading report: {str(e)}')
        return redirect('accounting:reports')


@login_required
@staff_required
def view_report(request, report_id):
    """View a generated financial report in the browser"""
    try:
        report = get_object_or_404(
            FinancialReport,
            id=report_id,
            generated_by=request.user,
            is_available=True
        )
        
        # Prepare context for rendering
        context = {
            'report': report,
            'report_data': report.report_data,
            'report_type': report.report_type,
            'period_name': report.period_name
        }
        
        # Choose template based on report type
        template_map = {
            'income_statement': 'accounting/report_templates/income_statement.html',
            'balance_sheet': 'accounting/report_templates/balance_sheet.html',
            'cash_flow': 'accounting/report_templates/cash_flow.html',
            'fee_collection': 'accounting/report_templates/fee_collection.html',
            'expense_report': 'accounting/report_templates/expense_report.html'
        }
        
        template = template_map.get(report.report_type, 'accounting/report_templates/generic.html')
        
        return render(request, template, context)
        
    except Exception as e:
        messages.error(request, f'Error viewing report: {str(e)}')
        return redirect('accounting:reports')


@login_required
def generate_income_statement(request):
    """Generate income statement for the current month"""
    from .report_utils import generate_income_statement

    try:
        report = generate_income_statement()
        messages.success(request, f'Income statement generated: {report.file.name}')
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')

    return redirect('accounting:reports')


@login_required
def generate_fee_collection_report(request):
    """Generate fee collection report for the current month"""
    from .report_utils import generate_fee_collection_report

    try:
        report = generate_fee_collection_report()
        messages.success(request, f'Fee collection report generated: {report.file.name}')
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')

    return redirect('accounting:reports')


def generate_expense_report(request):
    """Generate expense report for the current month"""
    from .report_utils import generate_expense_report

    try:
        report = generate_expense_report()
        messages.success(request, f'Expense report generated: {report.file.name}')
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')

    return redirect('accounting:reports')


@login_required
def dashboard_stats_ajax(request):
    """AJAX endpoint for dashboard statistics"""
    try:
        from django.db.models import Sum
        from datetime import datetime, timedelta
        
        # Get current month stats
        now = timezone.now()
        current_month_start = now.replace(day=1)
        
        # Calculate statistics
        total_fees = TuitionFee.objects.aggregate(
            total=Sum('amount_due')
        )['total'] or 0
        
        total_payments = Payment.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_expenses = Expense.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Current month stats
        monthly_payments = Payment.objects.filter(
            payment_date__gte=current_month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_expenses = Expense.objects.filter(
            date__gte=current_month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Outstanding fees
        outstanding_fees = TuitionFee.objects.filter(
            status='unpaid'
        ).aggregate(total=Sum('amount_due'))['total'] or 0
        
        # Report statistics
        total_reports = FinancialReport.objects.filter(
            generated_by=request.user
        ).count()
        
        reports_this_month = FinancialReport.objects.filter(
            generated_by=request.user,
            generated_at__gte=current_month_start
        ).count()

        stats = {
            'total_fees': float(total_fees),
            'total_payments': float(total_payments),
            'total_expenses': float(total_expenses),
            'monthly_payments': float(monthly_payments),
            'monthly_expenses': float(monthly_expenses),
            'outstanding_fees': float(outstanding_fees),
            'net_income': float(total_payments - total_expenses),
            'monthly_net': float(monthly_payments - monthly_expenses),
            'total_reports': total_reports,
            'reports_this_month': reports_this_month,
            'last_updated': now.isoformat()
        }
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching dashboard stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@staff_required
def recent_reports_ajax(request):
    """AJAX endpoint for recent reports"""
    try:
        # Get recent reports (last 10)
        recent_reports = FinancialReport.objects.filter(
            generated_by=request.user
        ).order_by('-generated_at')[:10]
        
        reports_data = []
        for report in recent_reports:
            reports_data.append({
                'id': str(report.id),
                'report_type': report.report_type,
                'period_name': report.period_name,
                'format': report.format,
                'created_at': report.generated_at.isoformat(),
                'file': bool(report.file),
                'download_count': report.download_count
            })
        
        return JsonResponse({
            'success': True,
            'reports': reports_data
        })
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching recent reports: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
