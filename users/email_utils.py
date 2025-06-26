from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

def send_welcome_email(user, password=None):
    """
    Send a welcome email to a newly created user.
    
    Args:
        user: The user object.
        password: Optional plaintext password to include in the email.
                 Only used for newly created users.
    """
    subject = 'Welcome to Glad Tidings School Portal'
    
    context = {
        'user': user,
        'temp_password': password,
        'school_name': 'Glad Tidings School',
        'support_email': settings.SCHOOL_SUPPORT_EMAIL,
        'login_url': settings.BASE_URL + reverse('login') if hasattr(settings, 'BASE_URL') else '/accounts/login/',
    }
    
    html_message = render_to_string('users/emails/welcome_email.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
    )
    return True

def send_password_reset_link(user, request=None):
    """
    Send a password reset link to a user.
    
    Args:
        user: The user object.
        request: Optional request object to generate absolute URLs.
    """
    subject = 'Password Reset for Glad Tidings School Portal'
    
    # Generate password reset token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Get base URL for reset link
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        current_site = get_current_site(request)
        domain = current_site.domain
        base_url = f'{protocol}://{domain}'
    else:
        base_url = getattr(settings, 'BASE_URL', 'http://gladtidingsschool.example')
    
    # Construct the reset URL
    reset_path = reverse('users:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    reset_url = f'{base_url}{reset_path}'
    
    context = {
        'user': user,
        'uid': uid,
        'token': token,
        'reset_url': reset_url,
        'school_name': 'Glad Tidings School',
        'support_email': settings.SCHOOL_SUPPORT_EMAIL,
    }
    
    html_message = render_to_string('users/emails/password_reset_email.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
    )
    return True

def send_password_change_notification(user):
    """
    Send a notification email when a user's password has been changed.
    
    Args:
        user: The user object.
    """
    subject = 'Your Password Has Been Changed'
    
    context = {
        'user': user,
        'school_name': 'Glad Tidings School',
        'support_email': settings.SCHOOL_SUPPORT_EMAIL,
    }
    
    html_message = render_to_string('users/emails/password_changed_email.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
    )
    return True
