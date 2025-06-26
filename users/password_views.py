from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView
)
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .email_utils import send_password_change_notification

User = get_user_model()

class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'users/emails/password_reset_email.html'
    subject_template_name = 'users/emails/password_reset_subject.txt'
    template_name = 'users/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('password_change_done')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Send notification email about password change
        try:
            send_password_change_notification(self.request.user)
        except Exception:
            # Don't block the password change if email fails
            pass
        return response

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'users/password_change_done.html'
