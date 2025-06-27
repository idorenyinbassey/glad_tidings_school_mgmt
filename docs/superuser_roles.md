# Superuser Role Management

## Issue: Superusers Being Created with 'student' Role

The `createsuperuser` management command was creating superusers with the default 'student' role instead of 'admin'.

## Fix Implemented

1. **Custom User Manager**: 
   - Added a `CustomUserManager` class that extends Django's built-in `UserManager`
   - Override the `create_superuser` method to ensure the role is set to 'admin'

2. **Data Migration**: 
   - Created a migration (`0002_update_superuser_roles.py`) to fix any existing superusers that were assigned the 'student' role

3. **Management Command**:
   - Added a `fix_superuser_roles` management command for manual fixing and reporting of superuser roles
   - Use it with: `python manage.py fix_superuser_roles`

4. **Tests**:
   - Added tests to verify that superusers are correctly created with the 'admin' role

## Additional Information

In a custom user model, when extending `AbstractUser` and adding custom fields with defaults, those defaults need special handling for commands like `createsuperuser`. The issue occurs because `createsuperuser` creates users differently than the normal `create_user`/`create_superuser` methods.

By implementing a custom manager, we ensure that regardless of how a superuser is created (through the command line or programmatically), they always get the correct 'admin' role.

## Troubleshooting

If you still experience issues with superuser roles:

1. Run the management command: `python manage.py fix_superuser_roles`
2. Verify your database has the proper roles with: `python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print([(u.username, u.is_superuser, u.role) for u in User.objects.filter(is_superuser=True)])"`
