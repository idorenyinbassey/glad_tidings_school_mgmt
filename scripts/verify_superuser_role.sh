#!/bin/bash
# Script to verify superuser role assignment

# Navigate to the project directory
cd "$(dirname "$0")"

# Create a test superuser
echo "Creating a test superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();

# Delete the test user if it exists
User.objects.filter(username='roletest').delete();

# Create a new superuser
user = User.objects.create_superuser('roletest', 'roletest@example.com', 'password123');
print(f'Created superuser with role: {user.role}');
print(f'Is superuser: {user.is_superuser}');
print(f'Is staff: {user.is_staff}');

# Verify the role is correct
if user.role == 'admin':
    print('SUCCESS: Superuser has correct admin role');
else:
    print(f'ERROR: Superuser has incorrect role: {user.role}');

# Clean up by deleting the test user
User.objects.filter(username='roletest').delete();
print('Test user deleted');
"

echo "Test complete."
