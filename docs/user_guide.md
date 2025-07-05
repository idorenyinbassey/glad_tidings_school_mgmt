# Glad Tidings School Management Portal - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [User Management](#user-management)
   - [Adding Users](#adding-users)
   - [Setting User Roles](#setting-user-roles)
   - [Managing User Profiles](#managing-user-profiles)
4. [Role-Based Features](#role-based-features)
   - [Student Features](#student-features)
   - [Staff Features](#staff-features)
   - [Admin Features](#admin-features)
   - [IT Support Features](#it-support-features)
5. [Academic Features](#academic-features)
   - [Class Timetable](#class-timetable)
   - [E-Library Resources](#e-library-resources)
   - [Announcements](#announcements)
   - [School Calendar](#school-calendar)
6. [Notification System](#notification-system)
7. [Profile Management](#profile-management)
8. [Technical Information](#technical-information)
9. [Result Management System](#result-management-system)

## Introduction

The Glad Tidings School Management Portal is a comprehensive system designed to manage all aspects of school operations. It provides role-specific dashboards for students, staff, administrators, and IT support personnel, with tailored features for each user type.

## System Overview

The portal includes the following main modules:

- **User Management**: Registration, authentication, and role assignment
- **Academics**: Course materials, timetables, e-library
- **Assignments**: Submission and grading
- **CBT (Computer-Based Testing)**: Online assessments
- **Accounting**: Fee management and financial records
- **IT Support**: Technical assistance requests
- **Notifications**: School-wide and personalized announcements
- **Performance Analytics**: Student progress tracking
- **Attendance**: Student and staff attendance tracking
- **Profile Management**: User profile settings

## User Management

### Adding Users

There are two ways to add users to the system:

#### 1. Using the Django Admin Interface

This method is recommended for administrators who need to add multiple users or set specific permissions.

1. Log in to the admin interface at `/admin/` with an admin account
2. Navigate to "Users" under the "Authentication and Authorization" section
3. Click "Add User"
4. Enter the required information (username and password)
5. Click "Save and continue editing"
6. Fill out additional user details (email, first name, last name)
7. Select the appropriate user permissions
8. Set the "Role" field to the appropriate value (student, staff, admin, it_support)
9. Click "Save"

#### 2. User Registration (for new users)

1. Direct new users to the registration page
2. Users fill out the registration form with their details
3. By default, new registrations are assigned the "student" role
4. An administrator can later change the user's role as needed

### Setting User Roles

To change a user's role:

1. Log in to the admin interface at `/admin/`
2. Navigate to "Users" under "Authentication and Authorization"
3. Click on the user you want to modify
4. Change the "Role" dropdown to the desired role:
   - `student`: For students
   - `staff`: For teachers and school staff
   - `admin`: For school administrators
   - `accountant`: For finance and accounting personnel
   - `it_support`: For technical support personnel
5. Click "Save"

### Managing User Profiles

After creating a basic user account, you should set up their profile:

#### For Students:

1. Log in to the admin interface
2. Navigate to "StudentProfiles" under the "Students" section
3. Click "Add StudentProfile"
4. Select the user from the dropdown
5. Fill in the required fields:
   - Admission Number
   - Date of Birth
   - Address (optional)
   - Guardian Name (optional)
   - Guardian Contact (optional)
6. Click "Save"

#### For Staff:

1. Log in to the admin interface
2. Navigate to "StaffProfiles" under the "Staff" section
3. Click "Add StaffProfile"
4. Select the user from the dropdown
5. Fill in the required fields:
   - Employee ID
   - Department
   - Designation
   - Date of Joining
6. Click "Save"

## Role-Based Features

### Student Features

Students have access to:
- Personal dashboard with upcoming assignments and announcements
- Course materials and resources
- Assignment submission system
- Performance analytics
- Attendance records
- Library resources
- Personal notifications

### Staff Features

Staff members have access to:
- Staff dashboard with class information and schedules
- Student management tools
- Assignment creation and grading
- Attendance recording
- E-library management
- Performance analytics for students
- Announcement creation

### Admin Features

Administrators have access to:
- Administrative dashboard with school-wide metrics
- User management
- Financial records and fee management
- School calendar management
- Report generation
- System configuration
- All features available to staff

### Accountant Features

Accountants have access to:
- Professional finance dashboard with real-time financial metrics
- Comprehensive fee management (create, edit, track student fees)
- Payment processing and recording
- Expense management and tracking
- Payroll management for staff
- Financial reporting and analytics
- Interactive charts and financial trends
- Quick actions for common financial tasks
- Student payment history and status tracking

**Note**: Accountants are automatically redirected to the specialized finance dashboard (`/accounting/`) upon login, providing a professional finance-focused interface rather than the general staff dashboard.

For detailed information about accounting features, see the [Accounting & Finance User Guide](accounting_finance_guide.md).

### IT Support Features

IT Support personnel have access to:
- IT dashboard with system status
- Technical support ticket management
- User assistance tools
- System diagnostics
- Resource monitoring

## Academic Features
// ...existing content...

## Result Management System 📊

The Result Management System provides comprehensive tools for managing student academic results from entry to publication.

### For Teachers/Staff:

#### Result Entry
1. Navigate to **Results → Enter Results**
2. Select academic session and term
3. Choose class and student
4. Select subject and assessment type
5. Enter score and teacher's remark
6. Save the result

#### Bulk Upload
1. Go to **Results → Bulk Upload**
2. Download CSV template
3. Fill in student results data
4. Upload the completed CSV file
5. Review and confirm uploads

#### Result Compilation
1. Access **Results → Compile Results**
2. Select session, term, and class
3. Choose subjects to compile
4. Generate term result sheets
5. Review and publish results

### For Students:

#### Viewing Results
1. Login to student dashboard
2. View recent results overview
3. Click **"View My Results"** for detailed view
4. Filter by session, term, or subject
5. See individual assessments and compiled grades

#### Printing Result Sheets
1. Go to **"My Result Sheets"**
2. Select academic session and term
3. View compiled result sheet
4. Download PDF for printing
5. Print professional result card

### Result Management Features:
- ✅ Individual result entry with validation
- ✅ Bulk CSV upload with error checking
- ✅ Automatic grade calculation and positioning
- ✅ Teacher remarks and feedback system
- ✅ Professional PDF result sheets
- ✅ Student self-service result viewing
- ✅ Real-time statistics and analytics
- ✅ Role-based access control

// ...existing content continues...
### Class Timetable

The timetable system allows for scheduling classes with the following information:
- Class name
- Day of the week
- Period
- Subject
- Teacher
- Start and end times

To add a new timetable entry:

1. Log in to the admin interface
2. Navigate to "ClassTimetables" under the "Academics" section
3. Click "Add ClassTimetable"
4. Fill in all required fields
5. Click "Save"

### E-Library Resources

The E-Library allows uploading and categorizing educational resources:

To add a new resource:

1. Log in to the admin interface
2. Navigate to "ELibraryResources" under "Academics"
3. Click "Add ELibraryResource"
4. Fill in the required fields:
   - Title
   - Author (optional)
   - Description (optional)
   - Resource Type (book, article, worksheet, video, audio, presentation, other)
   - Subject (optional)
   - Grade Level (optional)
   - Upload the file
   - Thumbnail (optional)
   - Check "Is Featured" if you want it to appear prominently
5. Click "Save"

### Announcements

To create a new announcement:

1. Log in to the admin interface
2. Navigate to "Announcements" under "Academics"
3. Click "Add Announcement"
4. Fill in the required fields:
   - Title
   - Message
   - Audience (everyone, students only, staff only, administrators only, parents only)
   - Priority (low, normal, high, urgent)
   - Is Active (check this to make the announcement visible)
   - Publish Date (optional - when the announcement should become visible)
   - Expiry Date (optional - when the announcement should no longer be visible)
   - Attachment (optional)
5. Click "Save"

### School Calendar

To add a calendar event:

1. Log in to the admin interface
2. Navigate to "SchoolCalendarEvents" under "Academics"
3. Click "Add SchoolCalendarEvent"
4. Fill in the required fields:
   - Title
   - Description (optional)
   - Start Date
   - End Date
5. Click "Save"

## Notification System

The notification system has two components:

1. **School-wide Announcements**: Visible to all users or specific user groups
2. **Personal Notifications**: Targeted to specific users

When an announcement is created, personal notifications are automatically generated for all relevant users based on the audience setting.

Users can:
- View all notifications on the Notifications page
- Mark notifications as read individually
- Mark all notifications as read at once
- Filter between personal notifications and school announcements

## Profile Management

The Glad Tidings School Management Portal offers a comprehensive profile management system where users can view and update their personal information.

### Accessing Your Profile

Users can access their profile by clicking on their name/avatar in the top navigation bar and selecting "My Profile". The profile page displays information relevant to the user's role and allows editing of specific fields.

### Updatable Information

- **All Users**: First name, last name, email address
- **Students**: Address, guardian name, guardian contact
- **Staff**: Position, phone number, address

### Profile Management Features

- **Form Validation**: Provides real-time feedback when updating profile information
- **Error Handling**: Clear error messages if profile updates encounter problems
- **Password Management**: Link to change password is available on the profile page

For detailed instructions on managing profiles, see the [Profile Management Guide](./profile_management_guide.md).

## Technical Information

### System Requirements

- Python 3.8 or higher
- Django 4.2.23
- PostgreSQL (recommended for production) or SQLite (development)
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Environment Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/Mac: `source .venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at: http://127.0.0.1:8000/

### Backup and Restore

It's recommended to regularly back up the database:

```bash
python manage.py dumpdata > backup.json
```

To restore from a backup:

```bash
python manage.py loaddata backup.json
```

### Running Tests

To run the test suite:

```bash
# Using pytest (recommended)
python -m pytest

# Using Django's test runner
python manage.py test
```

For running tests with coverage:

```bash
coverage run -m pytest
coverage report
coverage html  # Creates an HTML report in htmlcov/
```

You can run specific test categories using markers:

```bash
# Run only unit tests
python -m pytest -m unit

# Run only integration tests
python -m pytest -m integration
```

Or run tests from specific modules:

```bash
python -m pytest core/tests/test_urls.py
```

For more details on testing practices and organization, see the [Testing Guidelines](./testing_guidelines.md) document.

## Result Management System 📊

The Result Management System provides comprehensive tools for managing student academic results from entry to publication.

### For Teachers/Staff:

#### Result Entry
1. Navigate to **Results → Enter Results**
2. Select academic session and term
3. Choose class and student
4. Select subject and assessment type
5. Enter score and teacher's remark
6. Save the result

#### Bulk Upload
1. Go to **Results → Bulk Upload**
2. Download CSV template
3. Fill in student results data
4. Upload the completed CSV file
5. Review and confirm uploads

#### Result Compilation
1. Access **Results → Compile Results**
2. Select session, term, and class
3. Choose subjects to compile
4. Generate term result sheets
5. Review and publish results

### For Students:

#### Viewing Results
1. Login to student dashboard
2. View recent results overview
3. Click **"View My Results"** for detailed view
4. Filter by session, term, or subject
5. See individual assessments and compiled grades

#### Printing Result Sheets
1. Go to **"My Result Sheets"**
2. Select academic session and term
3. View compiled result sheet
4. Download PDF for printing
5. Print professional result card

### Result Management Features:
- ✅ Individual result entry with validation
- ✅ Bulk CSV upload with error checking
- ✅ Automatic grade calculation and positioning
- ✅ Teacher remarks and feedback system
- ✅ Professional PDF result sheets
- ✅ Student self-service result viewing
- ✅ Real-time statistics and analytics
- ✅ Role-based access control
