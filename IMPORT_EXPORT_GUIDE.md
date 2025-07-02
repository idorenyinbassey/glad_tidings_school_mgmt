# Django Admin Import/Export Guide

## Overview

The Glad Tidings School Management System now supports comprehensive CSV/Excel import and export functionality for:

1. **Users** (Students and Staff creation)
2. **Tuition Fees** (Student fee management)
3. **Payments** (Fee payment tracking)
4. **Payroll** (Staff salary management)
5. **Expenses** (School expense tracking)

## How to Access Import/Export

### In Django Admin Panel:

1. Navigate to **Django Admin** (usually `/admin/`)
2. Log in with admin credentials
3. Go to any of these sections:

   - **Users** → **Users** (for creating students/staff)
   - **Accounting** → **Tuition fees**
   - **Accounting** → **Payments**
   - **Accounting** → **Payrolls**
   - **Accounting** → **Expenses**

4. Look for **Import** and **Export** buttons at the top of the list page

## Import Process

### Step 1: Prepare Your Data

#### For User Creation (Students/Staff):

```csv
username,first_name,last_name,email,user_type,admission_number,class,staff_id,department,position
john.doe,John,Doe,john.doe@email.com,student,STU001,JSS1,,,
jane.smith,Jane,Smith,jane.smith@email.com,staff,,,STF001,Mathematics,Teacher
mary.johnson,Mary,Johnson,mary.johnson@email.com,student,STU002,JSS2,,,
```

**Required Fields for Students:**

- `user_type`: "student"
- `admission_number`: Unique student ID
- `class`: Student's class level

**Required Fields for Staff:**

- `user_type`: "staff"
- `staff_id`: Unique staff ID
- `department`: Staff department
- `position`: Job position

#### For Tuition Fees:

```csv
student_username,session,term,amount_due,due_date
john.doe,2024/2025,First Term,50000,2025-01-15
mary.johnson,2024/2025,First Term,50000,2025-01-15
```

#### For Payroll:

```csv
staff_username,month,year,amount
jane.smith,January,2025,80000
```

#### For Payments:

```csv
tuition_fee_id,amount,payment_date,method,receipt_number,notes
1,25000,2025-01-10,bank,RCP001,Partial payment for first term
```

#### For Expenses:

```csv
description,amount,date,category,receipt_number,vendor,notes
Office Supplies,5000,2025-01-08,supplies,EXP001,ABC Supplies Ltd,Stationery
```

### Step 2: Import Data

1. Click **Import** button in the admin panel
2. Choose your CSV/Excel file
3. Select the correct file format (CSV, XLS, XLSX)
4. Click **Submit**
5. **Preview** the import - check for errors
6. If everything looks good, click **Confirm import**

## Export Process

1. Go to any model list page in admin
2. Click **Export** button
3. Choose your preferred format:
   - **CSV** - For simple data exchange
   - **XLS** - Excel format (older)
   - **XLSX** - Excel format (newer)
4. File will be downloaded automatically

## Features and Benefits

### ✅ **Bulk User Creation**

- Create multiple students and staff at once
- Automatic profile creation based on user type
- Automatic group assignment (Students/Staff groups)
- Default password assignment (users must change on first login)

### ✅ **Data Validation**

- Prevents duplicate usernames
- Validates email formats
- Ensures required fields are provided
- Prevents data conflicts

### ✅ **Smart Relationships**

- Links tuition fees to existing students
- Associates payments with tuition fees
- Connects payroll to staff members

### ✅ **Comprehensive Export**

- Export existing data for backup
- Generate reports in Excel format
- Include calculated fields (balances, full names, etc.)

## Important Notes

### User Creation

- All new users get default password: `defaultpassword123`
- Users should change password on first login
- Student users automatically get StudentProfile created
- Staff users automatically get StaffProfile created
- Users are automatically added to appropriate groups

### Data Format Requirements

- Dates: Use `YYYY-MM-DD` format (e.g., 2025-01-15)
- Numbers: Use plain numbers without currency symbols
- User Types: Must be exactly "student" or "staff"
- Usernames: Must be unique across the system

### Error Handling

- Preview phase shows all potential errors
- Invalid data is highlighted before import
- No data is saved until you confirm the import
- Detailed error messages guide you to fix issues

## Security Considerations

### Access Control

- Only admin users can import/export data
- Import/export actions are logged
- Data validation prevents malicious imports

### Data Protection

- Exported files contain sensitive information
- Store downloaded files securely
- Delete export files after use
- Use secure file transfer methods

## Troubleshooting

### Common Issues

**1. "User already exists" Error**

- Solution: Ensure usernames are unique
- Check existing users before import

**2. "Student/Staff not found" Error**

- Solution: Ensure referenced users exist
- Import users before importing related data

**3. "Invalid date format" Error**

- Solution: Use YYYY-MM-DD format for all dates

**4. "Required field missing" Error**

- Solution: Ensure all required fields are provided
- Check the field requirements above

### Best Practices

1. **Start Small**: Test with a few records first
2. **Backup First**: Export existing data before large imports
3. **Validate Data**: Check your CSV in Excel before import
4. **Use Templates**: Use generated templates as starting points
5. **Preview Always**: Always use the preview feature

## Example Workflows

### Workflow 1: New School Year Setup

1. **Export** existing students to backup
2. **Prepare** new student list in CSV
3. **Import** new students (user_type: student)
4. **Import** tuition fees for new session
5. **Verify** all data is correct

### Workflow 2: Staff Management

1. **Export** current staff for records
2. **Prepare** new staff CSV with positions
3. **Import** new staff (user_type: staff)
4. **Import** payroll data for staff
5. **Review** staff profiles in admin

### Workflow 3: Payment Bulk Entry

1. **Export** outstanding tuition fees
2. **Prepare** payment CSV with receipts
3. **Import** payments data
4. **Verify** balance calculations

## Support

For technical support or questions about import/export functionality:

1. Check error messages in the preview phase
2. Verify your CSV format matches examples
3. Ensure all required fields are provided
4. Contact system administrator for complex issues

---

**Generated**: July 2, 2025
**System**: Glad Tidings School Management System
**Version**: Production Ready with Import/Export
