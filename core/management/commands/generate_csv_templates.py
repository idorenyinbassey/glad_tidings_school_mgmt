from django.core.management.base import BaseCommand
import csv
import os


class Command(BaseCommand):
    help = 'Generate sample CSV templates for importing data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='sample_data_templates',
            help='Directory to save CSV templates (default: sample_data_templates)'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generate User Import Template
        users_file = os.path.join(output_dir, 'users_import_template.csv')
        with open(users_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'username', 'first_name', 'last_name', 'email', 'user_type',
                'admission_number', 'class', 'staff_id', 'department', 'position'
            ])
            # Sample data
            writer.writerow([
                'john.doe', 'John', 'Doe', 'john.doe@email.com', 'student',
                'STU001', 'JSS1', '', '', ''
            ])
            writer.writerow([
                'jane.smith', 'Jane', 'Smith', 'jane.smith@email.com', 'staff',
                '', '', 'STF001', 'Mathematics', 'Teacher'
            ])
            writer.writerow([
                'mary.johnson', 'Mary', 'Johnson', 'mary.johnson@email.com', 'student',
                'STU002', 'JSS2', '', '', ''
            ])

        # Generate Tuition Fee Import Template
        tuition_file = os.path.join(output_dir, 'tuition_fees_import_template.csv')
        with open(tuition_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'student_username', 'session', 'term', 'amount_due', 'due_date'
            ])
            # Sample data
            writer.writerow([
                'john.doe', '2024/2025', 'First Term', '50000', '2025-01-15'
            ])
            writer.writerow([
                'mary.johnson', '2024/2025', 'First Term', '50000', '2025-01-15'
            ])

        # Generate Payroll Import Template
        payroll_file = os.path.join(output_dir, 'payroll_import_template.csv')
        with open(payroll_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'staff_username', 'month', 'year', 'amount'
            ])
            # Sample data
            writer.writerow([
                'jane.smith', 'January', '2025', '80000'
            ])

        # Generate Payment Import Template
        payment_file = os.path.join(output_dir, 'payments_import_template.csv')
        with open(payment_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'tuition_fee_id', 'amount', 'payment_date', 'method', 'receipt_number', 'notes'
            ])
            # Sample data
            writer.writerow([
                '1', '25000', '2025-01-10', 'bank', 'RCP001', 'Partial payment for first term'
            ])

        # Generate Expense Import Template
        expense_file = os.path.join(output_dir, 'expenses_import_template.csv')
        with open(expense_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'description', 'amount', 'date', 'category', 'receipt_number', 'vendor', 'notes'
            ])
            # Sample data
            writer.writerow([
                'Office Supplies', '5000', '2025-01-08', 'supplies',
                'EXP001', 'ABC Supplies Ltd', 'Stationery for office'
            ])

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated CSV templates in {output_dir}/ directory:\n'
                f'- {users_file}\n'
                f'- {tuition_file}\n'
                f'- {payroll_file}\n'
                f'- {payment_file}\n'
                f'- {expense_file}\n\n'
                f'Usage Instructions:\n'
                f'1. Fill in the CSV files with your data\n'
                f'2. Go to Django Admin panel\n'
                f'3. Navigate to the respective model (Users, Tuition Fees, etc.)\n'
                f'4. Click "Import" button to upload your CSV file\n'
                f'5. Preview and confirm the import\n\n'
                f'Notes:\n'
                f'- For users: user_type should be "student" or "staff"\n'
                f'- For students: provide admission_number and class\n'
                f'- For staff: provide staff_id, department, and position\n'
                f'- Dates should be in YYYY-MM-DD format\n'
                f'- All users will get default password "defaultpassword123" - ask them to change it'
            )
        )
