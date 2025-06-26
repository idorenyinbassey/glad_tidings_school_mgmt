"""
Management command to check user permissions and access
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class Command(BaseCommand):
    help = 'Check user permissions and roles'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Checking user permissions...'))
        
        # Check the accountant user
        try:
            accountant = User.objects.get(username='accountant')
            self.stdout.write(f"Accountant user: {accountant.username}")
            self.stdout.write(f"Role: {accountant.role}")
            self.stdout.write(f"Is staff: {accountant.is_staff}")
            self.stdout.write(f"Is superuser: {accountant.is_superuser}")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("Accountant user not found"))
            
        # Check if 'accountant' or 'Accountant' is a valid role
        all_roles = [choice[0] for choice in User.ROLES]
        self.stdout.write(f"Available roles: {all_roles}")
        
        if 'accountant' in all_roles:
            self.stdout.write(self.style.SUCCESS("'accountant' is a valid role"))
        else:
            self.stdout.write(self.style.WARNING("'accountant' is NOT a valid role"))
            
        # Check URL configuration
        try:
            accounting_url = reverse('accounting:accounting_home')
            self.stdout.write(f"Accounting URL: {accounting_url}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error with accounting URL: {e}"))
