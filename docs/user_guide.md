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

### IT Support Features

IT Support personnel have access to:
- IT dashboard with system status
- Technical support ticket management
- User assistance tools
- System diagnostics
- Resource monitoring

## Academic Features

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
- Django 5.2.3
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
./run_tests.sh all-fixed
```

Or for specific test categories:

```bash
./run_tests.sh [category]
```

Where category is one of: url, security, responsive, features, performance, forms, mobile, api
