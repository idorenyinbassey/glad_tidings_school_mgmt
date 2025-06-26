from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

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
