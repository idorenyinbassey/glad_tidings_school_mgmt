from django.shortcuts import redirect
from django.http import HttpResponse
from functools import wraps

def staff_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a staff member
    or admin.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        # Check if user has role 'staff' or 'admin'
        if not user.is_authenticated:
            return redirect('login')
        
        if not (user.role == 'staff' or user.role == 'admin' or user.is_superuser):
            return HttpResponse("You don't have permission to access this page.", status=403)
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def accountant_required(view_func):
    """
    Decorator for views that checks that the user is logged in and has the role 'accountant'.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')
        
        if not (user.role == 'accountant' or user.role == 'admin' or user.is_superuser):
            return HttpResponse("You don't have permission to access this page.", status=403)
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    """
    Decorator for views that checks that the user is logged in and has the role 'admin'.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')
        
        if not (user.role == 'admin' or user.is_superuser):
            return HttpResponse("You don't have permission to access this page.", status=403)
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
