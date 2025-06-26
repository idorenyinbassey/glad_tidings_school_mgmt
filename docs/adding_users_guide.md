# Quick Guide: Adding Users to Glad Tidings School Portal

This guide provides step-by-step instructions for adding users with different roles to the Glad Tidings School Management Portal.

> **Important Update**: We have enhanced the profile management system. Users can now update their profile information including name, email, address, phone number, guardian information, etc. directly from their profile page. These changes will be automatically saved in the database.
>
> **Email Notifications**: New users now receive welcome emails with login credentials, and all users can reset their passwords via email.

## Adding Users via Django Admin

### Step 1: Access the Admin Interface
1. Log in to the admin interface at `/admin/` with an administrator account
2. You'll see the Django admin dashboard with various models grouped by application

### Step 2: Create a New User
1. Under "USERS" section, click on "Users"
2. Click the "ADD USER +" button in the top right corner
3. Enter the following required information:
   - Username
   - Password (and password confirmation)
4. Click "Save and continue editing"

### Step 3: Set User Role and Information
On the user edit page:
1. Fill out personal information:
   - First name
   - Last name
   - Email address (required for email notifications)
2. Set the user role in the dropdown field labeled "Role":
   - Select "Student" for student users
   - Select "Staff" for teachers and staff members
   - Select "Admin" for school administrators
   - Select "IT Support" for technical support personnel
3. For admin users, also check the "Staff status" checkbox to grant admin site access
4. Click "Save" to confirm the changes
   - **Note**: For new users, a welcome email is automatically sent to the email address provided

### Step 4: Create Associated Profile

#### For Student Users:
1. Navigate to "Students" > "Student profiles"
2. Click "ADD STUDENT PROFILE +"
3. Fill out the required fields:
   - User: Select the user you just created
   - Admission Number: Enter a unique ID for the student
   - Date of Birth: Enter the student's birth date
   - Address: (Optional) Student's address
   - Guardian Name: (Optional) Parent or guardian name
   - Guardian Contact: (Optional) Guardian's phone number
4. Click "Save"

#### For Staff Users:
1. Navigate to "Staff" > "Staff profiles"
2. Click "ADD STAFF PROFILE +"
3. Fill out the required fields:
   - User: Select the user you just created
   - Employee ID: Enter a unique ID for the staff member
   - Department: Select or enter their department
   - Position: Enter their job title
   - Date of Joining: Enter their hire date
4. Click "Save"

#### For Admin and IT Support:
- Additional profiles are not strictly required but may be created in the Staff profiles section as needed

## Bulk User Import (for Administrators)

For adding multiple users at once:

### Using Django Management Command
1. Create a CSV file with user data (username, email, first_name, last_name, role)
2. Use the management command:
   ```bash
   python manage.py import_users path/to/your/csv_file.csv
   ```

### Using the Admin Interface Batch Upload
1. Navigate to "Users" > "Import users"
2. Select your CSV file with the user data
3. Map the columns to the appropriate fields
4. Click "Import" to create all users

## Role-Specific Information

### Student Users
- Default dashboard: Student Dashboard
- Can access: Assignments, Results, E-Library, Attendance
- Cannot access: Admin site, Staff features

### Staff Users
- Default dashboard: Staff Dashboard
- Can access: Student data, Assignments, Grading, Attendance recording
- Cannot access: Admin features unless specifically granted

### Admin Users
- Default dashboard: Admin Dashboard
- Full access to all features
- Can manage users, finances, and system settings
- Automatically granted access to the admin site

### IT Support Users
- Default dashboard: IT Support Dashboard
- Can access: Technical support tickets, User management
- Focus on system maintenance and technical assistance

## Password Management

### Setting Initial Password
When creating a user, you can:
1. Set a temporary password during creation
   - When a new user is created, a welcome email with login credentials is automatically sent
   - The welcome email includes their username and temporary password
   - The user will be instructed to change their password on first login

When editing an existing user, you can:
1. Choose the "Send welcome email to user" option in the user edit form
   - This will send a welcome email with instructions to the user (without changing their password)

### Password Reset
Users can reset their passwords by:
1. Clicking "Forgot Password" on the login page
2. Entering their email address
3. Following the link in the password reset email sent to them
   - The reset link is valid for 24 hours
   - After resetting their password, users will receive a confirmation email

### Force Password Reset
As an administrator, you can send password reset emails:
1. Go to Users in the admin panel
2. Select one or more users
3. Choose "Send password reset email to selected users" from the actions dropdown
4. Click "Go" to send reset emails to all selected users

### Admin Bulk Actions for Emails
The following email-related actions are available in the user admin:
- **Send welcome email to selected users**: Generates a temporary password and sends welcome emails
- **Send password reset email to selected users**: Sends password reset links to selected users

## User Status Management

### Deactivating a User
To temporarily disable a user account:
1. Edit the user in the admin interface
2. Uncheck the "Active" checkbox
3. Click "Save"

### Reactivating a User
To reactivate a disabled account:
1. Go to Users and filter by "Inactive"
2. Edit the inactive user
3. Check the "Active" checkbox
4. Click "Save"

## Support and Troubleshooting

If you encounter any issues adding users:
1. Check that the username is unique
2. Ensure email addresses are in correct format
3. Verify that required fields for profiles are completed
4. Contact the system administrator for assistance

If you encounter any issues with email notifications:
1. Verify the user has a valid email address in their profile
2. Check the email configuration in the system settings
3. For development environments, check the console for email output
4. In production, check the email sending service logs

For technical support, contact:
- Email: support@gladtidingsschool.example
- Phone: 555-TECH-HELP
