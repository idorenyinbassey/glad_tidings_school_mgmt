from django.db import migrations

def update_superuser_roles(apps, schema_editor):
    # Get the historical model
    CustomUser = apps.get_model('users', 'CustomUser')
    
    # Find all superusers with 'student' role and update them to 'admin'
    for user in CustomUser.objects.filter(is_superuser=True, role='student'):
        user.role = 'admin'
        user.save()

def reverse_superuser_roles(apps, schema_editor):
    # This is a no-op as we don't want to revert superusers back to 'student' role
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_superuser_roles, reverse_superuser_roles),
    ]
