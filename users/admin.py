from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django import forms
from import_export.admin import ImportExportModelAdmin
from core.resources import UserResource
from .models import CustomUser
from .email_utils import send_welcome_email, send_password_reset_link

class SendWelcomeEmailForm(forms.Form):
    """Form for sending welcome emails to users."""
    subject = forms.CharField(max_length=255, initial="Welcome to Glad Tidings School Portal")
    include_password = forms.BooleanField(
        label="Generate and include a temporary password",
        required=False,
        initial=True
    )

class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    resource_class = UserResource
    fieldsets = UserAdmin.fieldsets + (
        ('Role info', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role info', {'fields': ('role', 'email')}),
    )
    list_display = UserAdmin.list_display + ('role', 'email')
    list_filter = UserAdmin.list_filter + ('role',)
    actions = ['send_welcome_email_action', 'send_password_reset']

    # Add a field to the user creation form to control email sending
    def get_form(self, request, obj=None, **kwargs):
        # Use exclude parameter if provided or initialize it
        kwargs.setdefault('fields', [])

        # Get the form without the non-model field
        form = super().get_form(request, obj, **kwargs)

        # If this is a change form, add the non-model field manually
        if obj is not None:  # Change form (not add form)
            # Create a clean copy of base_fields to avoid modifying the original
            if not hasattr(form, 'declared_fields'):
                form.declared_fields = {}

            form.declared_fields['send_welcome_email_option'] = forms.BooleanField(
                label=_("Send welcome email to user"),
                required=False,
                initial=False,
                help_text=_("Send a welcome email to the user with login instructions.")
            )

        return form

    def save_model(self, request, obj, form, change):
        """Override save_model to handle sending welcome emails."""
        # Check if this is a new user
        is_new_user = not obj.pk

        # Generate random password if it's a new user
        temp_password = None
        if is_new_user:
            temp_password = CustomUser.objects.make_random_password()
            obj.set_password(temp_password)

        # Save the user object
        super().save_model(request, obj, form, change)

        # Send welcome email if requested for new users
        if is_new_user and obj.email:
            # Always send welcome email for new users
            try:
                send_welcome_email(obj, temp_password)
                messages.success(request, f"Welcome email sent to {obj.email}.")
            except Exception as e:
                messages.error(request, f"Failed to send welcome email: {str(e)}")
        elif not change and form.cleaned_data.get('send_welcome_email_option', False) and obj.email:
            # Send welcome email for existing users if the option is selected
            try:
                send_welcome_email(obj)
                messages.success(request, f"Welcome email sent to {obj.email}.")
            except Exception as e:
                messages.error(request, f"Failed to send welcome email: {str(e)}")

    # Action to send welcome emails to selected users
    @admin.action(description="Send welcome email to selected users")
    def send_welcome_email_action(self, request, queryset):
        """Send welcome emails to selected users."""
        email_count = 0
        for user in queryset:
            if user.email:
                try:
                    # Generate a new password only when explicitly requested
                    temp_password = CustomUser.objects.make_random_password()
                    user.set_password(temp_password)
                    user.save()

                    send_welcome_email(user, temp_password)
                    email_count += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f"Failed to send email to {user.email}: {e}",
                        level=messages.ERROR
                    )

        if email_count:
            self.message_user(
                request,
                f"Welcome emails sent to {email_count} users.",
                level=messages.SUCCESS
            )

    # Action to send password reset emails to selected users
    @admin.action(description="Send password reset email to selected users")
    def send_password_reset(self, request, queryset):
        """Send password reset emails to selected users."""
        email_count = 0

        for user in queryset:
            if user.email:
                try:
                    # Use our custom password reset function
                    send_password_reset_link(user, request)
                    email_count += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f"Failed to send password reset to {user.email}: {e}",
                        level=messages.ERROR
                    )

        if email_count:
            self.message_user(
                request,
                f"Password reset emails sent to {email_count} users.",
                level=messages.SUCCESS
            )

# Register the custom admin class
admin.site.register(CustomUser, CustomUserAdmin)
