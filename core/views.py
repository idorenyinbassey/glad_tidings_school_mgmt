from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.template import loader
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def landing_page(request):
    return render(request, 'core/landing.html')

def about_us(request):
    return render(request, 'core/about_us.html')

def admission(request):
    return render(request, 'core/admission.html')

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
        return render(request, 'core/dashboard_student.html')
    elif role == 'staff':
        return render(request, 'core/dashboard_staff.html')
    elif role == 'admin':
        return render(request, 'core/dashboard_admin.html')
    elif role == 'it_support':
        return render(request, 'core/dashboard_it.html')
    else:
        return render(request, 'core/dashboard.html')


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
