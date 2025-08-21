from import_export import resources, fields
from django.contrib.auth.models import Group
from users.models import CustomUser
from students.models import StudentProfile
from staff.models import StaffProfile
from accounting.models import TuitionFee, Payment, Payroll, Expense


class UserResource(resources.ModelResource):
    """Resource for importing/exporting Users with role assignment"""

    # Custom fields for user type identification
    user_type = fields.Field(
        column_name='user_type',
        attribute='user_type',
        readonly=False
    )

    # Additional profile fields for students
    admission_number = fields.Field(
        column_name='admission_number',
        attribute='admission_number',
        readonly=False
    )
    student_class = fields.Field(
        column_name='class',
        attribute='student_class',
        readonly=False
    )

    # Additional profile fields for staff
    staff_id = fields.Field(
        column_name='staff_id',
        attribute='staff_id',
        readonly=False
    )
    department = fields.Field(
        column_name='department',
        attribute='department',
        readonly=False
    )
    position = fields.Field(
        column_name='position',
        attribute='position',
        readonly=False
    )

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'user_type', 'admission_number', 'student_class',
            'staff_id', 'department', 'position', 'is_active'
        )
        export_order = fields
        import_id_fields = ('username',)

    def dehydrate_user_type(self, user):
        """Determine user type for export"""
        if hasattr(user, 'studentprofile'):
            return 'student'
        elif hasattr(user, 'staffprofile'):
            return 'staff'
        return 'admin'

    def dehydrate_admission_number(self, user):
        """Export student admission number"""
        if hasattr(user, 'studentprofile'):
            return user.studentprofile.admission_number
        return None

    def dehydrate_student_class(self, user):
        """Export student class"""
        if hasattr(user, 'studentprofile'):
            return user.studentprofile.current_class
        return None

    def dehydrate_staff_id(self, user):
        """Export staff ID"""
        if hasattr(user, 'staffprofile'):
            return user.staffprofile.staff_id
        return None

    def dehydrate_department(self, user):
        """Export staff department"""
        if hasattr(user, 'staffprofile'):
            return user.staffprofile.department
        return None

    def dehydrate_position(self, user):
        """Export staff position"""
        if hasattr(user, 'staffprofile'):
            return user.staffprofile.position
        return None

    def before_import_row(self, row, **kwargs):
        """Process row before import"""
        # Generate username if not provided
        if not row.get('username'):
            first_name = row.get('first_name', '').lower()
            last_name = row.get('last_name', '').lower()
            if first_name and last_name:
                row['username'] = f"{first_name}.{last_name}"

    def after_save_instance(self, instance, new, row_number=None, **kwargs):
        """Create profile and assign groups after saving user"""
        user_type = getattr(instance, 'user_type', None)

        if user_type == 'student':
            # Create or update student profile
            student_profile, created = StudentProfile.objects.get_or_create(
                user=instance,
                defaults={
                    'admission_number': getattr(instance, 'admission_number', ''),
                    'current_class': getattr(instance, 'student_class', ''),
                    'date_of_birth': None,
                    'address': '',
                    'phone_number': '',
                    'guardian_name': '',
                    'guardian_phone': '',
                }
            )
            if not created:
                # Update existing profile
                if hasattr(instance, 'admission_number'):
                    student_profile.admission_number = instance.admission_number
                if hasattr(instance, 'student_class'):
                    student_profile.current_class = instance.student_class
                student_profile.save()

            # Add to Students group
            students_group, _ = Group.objects.get_or_create(name='Students')
            instance.groups.add(students_group)

        elif user_type == 'staff':
            # Create or update staff profile
            staff_profile, created = StaffProfile.objects.get_or_create(
                user=instance,
                defaults={
                    'staff_id': getattr(instance, 'staff_id', ''),
                    'department': getattr(instance, 'department', ''),
                    'position': getattr(instance, 'position', ''),
                    'date_of_birth': None,
                    'hire_date': None,
                    'phone_number': '',
                    'address': '',
                    'salary': 0,
                }
            )
            if not created:
                # Update existing profile
                if hasattr(instance, 'staff_id'):
                    staff_profile.staff_id = instance.staff_id
                if hasattr(instance, 'department'):
                    staff_profile.department = instance.department
                if hasattr(instance, 'position'):
                    staff_profile.position = instance.position
                staff_profile.save()

            # Add to Staff group
            staff_group, _ = Group.objects.get_or_create(name='Staff')
            instance.groups.add(staff_group)


class TuitionFeeResource(resources.ModelResource):
    """Resource for importing/exporting Tuition Fees"""
    
    class Meta:
        model = TuitionFee
        fields = (
            'id', 'student__user__username', 'student__user__first_name',
            'student__user__last_name', 'student__admission_number',
            'academic_year', 'term', 'total_amount', 'amount_paid',
            'balance', 'due_date', 'created_at'
        )
        export_order = fields


class PayrollResource(resources.ModelResource):
    """Resource for importing/exporting Payroll records"""
    
    class Meta:
        model = Payroll
        fields = (
            'id', 'staff__user__username', 'staff__user__first_name',
            'staff__user__last_name', 'staff__staff_id', 'staff__department',
            'month', 'year', 'basic_salary', 'allowances', 'deductions',
            'gross_salary', 'net_salary', 'created_at'
        )
        export_order = fields


class PaymentResource(resources.ModelResource):
    """Resource for importing/exporting Payment records"""
    
    class Meta:
        model = Payment
        fields = (
            'id', 'tuition_fee__student__user__username',
            'tuition_fee__student__user__first_name',
            'tuition_fee__student__user__last_name',
            'tuition_fee__student__admission_number',
            'amount', 'payment_method', 'reference_number',
            'payment_date', 'created_at'
        )
        export_order = fields


class ExpenseResource(resources.ModelResource):
    """Resource for importing/exporting Expense records"""
    
    class Meta:
        model = Expense
        fields = (
            'id', 'category', 'description', 'amount',
            'date', 'created_by__username', 'created_at'
        )
        export_order = fields
