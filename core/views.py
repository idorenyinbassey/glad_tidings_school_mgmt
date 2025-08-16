from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.template import loader
from django.conf import settings
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
import logging
import json
from django.contrib import messages
from .forms import AdmissionApplicationForm, ContactForm
from .models import InboxMessage

logger = logging.getLogger(__name__)

def landing_page(request):
    """Landing page with latest news and upcoming events using core CMS models."""
    from .models import NewsPost, UpcomingEvent

    now_dt = timezone.now()
    # Latest news: published NewsPost
    latest_news = NewsPost.objects.filter(is_published=True).order_by('-published_at')[:2]

    # Upcoming events: events that haven't ended yet (or start in future)
    upcoming_events = UpcomingEvent.objects.filter(
        is_published=True
    ).filter(
        Q(end_time__gte=now_dt) | Q(start_time__gte=now_dt)
    ).order_by('start_time')[:3]

    return render(
        request,
        'core/landing.html',
        {'latest_news': latest_news, 'upcoming_events': upcoming_events}
    )

def about_us(request):
    return render(request, 'core/about_us.html')

def admission(request):
    # Handle admission application submission
    if request.method == 'POST':
        form = AdmissionApplicationForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            # metadata
            obj.source_page = 'admission'
            obj.source_ip = request.META.get('REMOTE_ADDR')
            obj.user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
            if request.user.is_authenticated:
                obj.submitted_by = request.user
            obj.save()
            messages.success(request, 'Your application has been submitted successfully. We will contact you soon.')
            return redirect('admission')
        else:
            messages.error(request, 'Please correct the errors in the form and try again.')
    else:
        form = AdmissionApplicationForm()
    return render(request, 'core/admission.html', {'admission_form': form})

def academics_page(request):
    return render(request, 'core/academics.html')

def portal(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')

@login_required
def dashboard(request):
    user = request.user
    role = getattr(user, 'role', None)
    
    if role == 'student':
        context = get_student_dashboard_context(user)
        return render(request, 'core/dashboard_student.html', context)
    elif role == 'staff':
        return render(request, 'core/dashboard_staff.html')
    elif role == 'admin':
        # Get live data for admin dashboard
        context = get_admin_dashboard_context()
        return render(request, 'core/dashboard_admin.html', context)
    elif role == 'accountant':
        return redirect('accounting:home')  # Redirect accountants to the finance dashboard
    elif role == 'it_support':
        return render(request, 'core/dashboard_it.html')
    else:
        return render(request, 'core/dashboard.html')


def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.source_page = 'contact'
            obj.source_ip = request.META.get('REMOTE_ADDR')
            obj.user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
            if request.user.is_authenticated:
                obj.submitted_by = request.user
            obj.save()
            messages.success(request, 'Thanks for reaching out! Your message has been received.')
            return redirect('contact_us')
        else:
            messages.error(request, 'Please correct the errors and try again.')
    else:
        form = ContactForm()
    return render(request, 'core/contact_us.html', {'form': form})


def custom_404(request, exception):
    """Custom 404 error handler"""
    logger.warning(f"404 error: {request.path} - User: {request.user}")
    
    template = loader.get_template('errors/404.html')
    context = {
        'request_path': request.path,
        'user': request.user,
    }
    
    return HttpResponseNotFound(template.render(context, request))


def custom_500(request):
    """Custom 500 error handler"""
    logger.error(f"500 error on {request.path} - User: {request.user}")
    
    template = loader.get_template('errors/500.html')
    context = {
        'request_path': request.path,
        'user': request.user,
        'debug': settings.DEBUG,
    }
    
    return HttpResponseServerError(template.render(context, request))


def custom_403(request, exception):
    """Custom 403 error handler"""
    logger.warning(f"403 error: {request.path} - User: {request.user}")
    
    template = loader.get_template('errors/403.html')
    context = {
        'request_path': request.path,
        'user': request.user,
    }
    
    return HttpResponseServerError(template.render(context, request))


def get_admin_dashboard_context():
    """Get live data for admin dashboard"""
    from django.db.models import Sum, Count, Avg
    from students.models import StudentProfile
    from staff.models import StaffProfile
    from accounting.models import TuitionFee, Payment, Expense
    from django.contrib.auth.models import User
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    current_year_start = today.replace(month=1, day=1)
    
    # Student Statistics
    total_students = StudentProfile.objects.filter(user__is_active=True).count()
    
    # Staff Statistics
    total_staff = StaffProfile.objects.filter(user__is_active=True).count()
    
    # Fee Collection Statistics
    total_fees_due = TuitionFee.objects.aggregate(total=Sum('amount_due'))['total'] or 0
    total_fees_paid = TuitionFee.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
    collection_rate = (total_fees_paid / total_fees_due * 100) if total_fees_due > 0 else 0
    
    # Monthly Revenue
    monthly_revenue = Payment.objects.filter(
        payment_date__gte=current_month_start,
        payment_date__lte=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Monthly Expenses
    monthly_expenses = Expense.objects.filter(
        date__gte=current_month_start,
        date__lte=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Recent Activities (based on actual data)
    recent_activities = []
    
    # Recent payments
    recent_payments = Payment.objects.select_related('tuition_fee__student__user').order_by('-payment_date')[:2]
    for payment in recent_payments:
        days_ago = (today - payment.payment_date).days
        time_ago = f"{days_ago} day{'s' if days_ago != 1 else ''} ago" if days_ago > 0 else "Today"
        recent_activities.append({
            'time': time_ago,
            'content': f'Fee payment of ₦{payment.amount:,.0f} received from {payment.tuition_fee.student.user.get_full_name()}',
            'type': 'payment'
        })
    
    # Recent expenses
    recent_expenses = Expense.objects.order_by('-date')[:2]
    for expense in recent_expenses:
        days_ago = (today - expense.date).days
        time_ago = f"{days_ago} day{'s' if days_ago != 1 else ''} ago" if days_ago > 0 else "Today"
        recent_activities.append({
            'time': time_ago,
            'content': f'Expense recorded: {expense.description} - ₦{expense.amount:,.0f}',
            'type': 'expense'
        })
    
    # Recent registrations
    recent_students = StudentProfile.objects.order_by('-created_at')[:2]
    for student in recent_students:
        created_date = student.created_at.date() if getattr(student, 'created_at', None) else today
        days_ago = (today - created_date).days
        time_ago = f"{days_ago} day{'s' if days_ago != 1 else ''} ago" if days_ago > 0 else "Today"
        recent_activities.append({
            'time': time_ago,
            'content': f'New student registration: {student.user.get_full_name()} - {student.admission_number}',
            'type': 'registration'
        })
    
    # Sort activities by most recent
    recent_activities = sorted(recent_activities, key=lambda x: x['time'])[:4]
    
    # Outstanding fees count
    students_with_outstanding = TuitionFee.objects.filter(
        status__in=['unpaid', 'partial']
    ).values('student').distinct().count()
    
    # Attendance rate (placeholder - would need actual attendance data)
    attendance_rate = 87  # This would be calculated from actual attendance records
    
    # Pending tasks (based on actual data)
    pending_tasks = []
    
    # Unpaid payroll
    from accounting.models import Payroll
    unpaid_payroll_count = Payroll.objects.filter(paid=False).count()
    if unpaid_payroll_count > 0:
        pending_tasks.append({
            'name': 'Unpaid Payroll',
            'count': unpaid_payroll_count,
            'badge_class': 'bg-danger',
            'url': '/accounting/payroll/'
        })
    
    # Students with outstanding fees
    if students_with_outstanding > 0:
        pending_tasks.append({
            'name': 'Outstanding Fees',
            'count': students_with_outstanding,
            'badge_class': 'bg-warning',
            'url': '/accounting/fees/'
        })
    
    # Recent expenses to approve (expenses over certain amount)
    high_value_expenses = Expense.objects.filter(
        amount__gte=50000,
        date__gte=today - timedelta(days=7)
    ).count()
    if high_value_expenses > 0:
        pending_tasks.append({
            'name': 'High-Value Expenses',
            'count': high_value_expenses,
            'badge_class': 'bg-info',
            'url': '/accounting/expenses/'
        })
    
    # Chart data for performance overview (6-month trend)
    chart_data = {
        'months': [],
        'revenue': [],
        'expenses': [],
        'students': []
    }
    
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
        
        # Student count (approximate - would need historical data)
        month_students = total_students  # Simplified - in reality, track historical data
        
        chart_data['months'].append(month_date.strftime('%b'))
        chart_data['revenue'].append(float(month_revenue))
        chart_data['expenses'].append(float(month_expenses))
        chart_data['students'].append(month_students)
    
    return {
        'total_students': total_students,
        'total_staff': total_staff,
        'attendance_rate': attendance_rate,
        'collection_rate': round(collection_rate, 1),
        'total_fees_paid': total_fees_paid,
        'total_fees_due': total_fees_due,
        'monthly_revenue': monthly_revenue,
        'monthly_expenses': monthly_expenses,
        'recent_activities': recent_activities,
        'pending_tasks': pending_tasks,
        'students_with_outstanding': students_with_outstanding,
        'chart_data': json.dumps(chart_data),
        'last_updated': today.strftime('%B %d, %Y')
    }


def get_student_dashboard_context(user):
    """Get live data for student dashboard"""
    try:
        from students.models import StudentProfile
        from results.models import StudentResult
        
        # Get student profile
        student_profile = StudentProfile.objects.get(user=user)
        
        # Get recent results (last 5)
        recent_results = StudentResult.objects.filter(
            student=student_profile
        ).select_related(
            'subject', 'assessment', 'session', 'term'
        ).order_by('-entered_at')[:5]
        
        return {
            'student_profile': student_profile,
            'recent_results': recent_results,
        }
    except StudentProfile.DoesNotExist:
        return {
            'student_profile': None,
            'recent_results': [],
        }
    except Exception as e:
        logger.error(f"Error getting student dashboard context: {e}")
        return {
            'student_profile': None,
            'recent_results': [],
        }


# Public listing pages
def news_list(request):
    """List published news posts (core CMS)."""
    from .models import NewsPost

    qs = NewsPost.objects.filter(is_published=True).order_by('-published_at')
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page') or 1)
    return render(request, 'core/news_list.html', {'page_obj': page_obj})


def events_list(request):
    """List upcoming events from core CMS."""
    from .models import UpcomingEvent

    now_dt = timezone.now()
    qs = UpcomingEvent.objects.filter(is_published=True)
    qs = qs.filter(Q(end_time__gte=now_dt) | Q(start_time__gte=now_dt)).order_by('start_time')
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page') or 1)
    return render(request, 'core/events_list.html', {'page_obj': page_obj})
