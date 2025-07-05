from django.shortcuts import redirect
from django.http import HttpResponse
from functools import wraps

def staff_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a staff member,
    accountant, or admin.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        # Check if user has role 'staff', 'accountant', or 'admin'
        if not user.is_authenticated:
            return redirect('login')
        
        if not (user.role in ['staff', 'accountant', 'admin'] or user.is_superuser):
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
            # Redirect to their appropriate dashboard instead of showing error
            if user.role == 'student':
                return redirect('dashboard')
            elif user.role == 'staff':
                return redirect('dashboard')
            elif user.role == 'it_support':
                return redirect('dashboard')
            else:
                error_msg = ("You don't have permission to access this page. "
                            "Only accountants and administrators can access financial modules.")
                return HttpResponse(error_msg, status=403)
            
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


def role_required(allowed_roles):
    """
    Decorator for views that checks that the user is logged in and has one of the allowed roles.
    Usage: @role_required(['staff', 'admin'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('login')
            
            # Check if user has one of the allowed roles or is superuser
            if not (hasattr(user, 'role') and user.role in allowed_roles) and not user.is_superuser:
                error_msg = f"You don't have permission to access this page. Required roles: {', '.join(allowed_roles)}"
                return HttpResponse(error_msg, status=403)
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
