from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Fix any superusers that have incorrect "student" roles'

    def handle(self, *args, **options):
        # Find all superusers
        superusers = User.objects.filter(is_superuser=True)
        
        # Count how many superusers are incorrectly marked as students
        incorrect_roles = superusers.filter(role='student').count()
        
        if incorrect_roles > 0:
            # Update all superusers to have 'admin' role
            superusers.filter(role='student').update(role='admin')
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {incorrect_roles} superuser(s) from "student" role to "admin" role')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('All superusers already have correct roles. No changes needed.')
            )
        
        # Print summary of all superusers
        self.stdout.write('\nSuperuser summary:')
        for user in superusers:
            self.stdout.write(f'Username: {user.username}, Role: {user.role}, Email: {user.email}')
