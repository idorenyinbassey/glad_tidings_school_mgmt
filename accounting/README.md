# Glad Tidings School Management System

## Accounting Module Documentation

The accounting module handles financial operations within the school management system including:
- Tuition fee management
- Payment tracking
- Financial reporting
- Expense tracking
- Payroll management

## User Roles & Access

- **Admin**: Full access to all accounting features
- **Staff**: Access to view reports and fee information
- **Accountant**: Access to manage fees, payments, and reports

## Key Components

### Models

1. **TuitionFee**
   - Tracks student fees, payment status, and due dates
   - Properties for outstanding amounts and payment percentages
   - Static methods for fee statistics

2. **Payment**
   - Records individual payments against tuition fees
   - Links to student records
   - Maintains payment history

3. **Expense**
   - Tracks school expenses by category
   - Used for financial reporting

4. **Payroll**
   - Manages staff salary payments
   - Tracks payment status

### Template Filters

Custom template filters for financial calculations and formatting:
- `div`: Division operation for calculations
- `mul`: Multiplication operation
- `sub`: Subtraction operation
- `percentage`: Formats a value as a percentage
- `currency`: Formats a value as Nigerian currency (₦)

## Development Guidelines

### Running Tests

To run all accounting tests:
```bash
python manage.py test accounting
```

To run specific test files:
```bash
python manage.py test accounting.tests.test_models
python manage.py test accounting.tests.test_views
```

### Adding Template Filters

1. Add new filters to `accounting/templatetags/accounting_filters.py`
2. Register with `@register.filter(name='filter_name')`
3. Add tests in `accounting/tests/test_templatetags.py`
4. Clear the template cache after changes:
   ```bash
   python manage.py clear_template_cache
   ```

### Common Issues

If template filters aren't recognized:
1. Ensure templates are loading the filters with `{% load accounting_filters %}`
2. Verify the templatetags directory has `__init__.py`
3. Clear the template cache
4. Restart the development server
