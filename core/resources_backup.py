from import_export import resources, fields, widgets
from import_export.widgets import ForeignKeyWidget
from django.contrib.auth.models import User, Group
from students.models import StudentProfile
from staff.models import StaffProfile
from accounting.models import TuitionFee, Payment, Payroll, Expense
from academics.models import (
    AcademicSession, AcademicTerm, Subject, StudentResult, TermResult
)
from cbt.models import CBTExam, CBTSession


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
        model = User
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

    def after_save_instance(self, instance, using_transactions, dry_run, **kwargs):
        """Create profile and assign groups after saving user"""
        if not dry_run:
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

    def before_save_instance(self, instance, using_transactions, dry_run, **kwargs):
        """Set custom attributes before saving"""
        row = kwargs.get('row', {})

        # Store custom attributes for use in after_save_instance
        instance.user_type = row.get('user_type')
        instance.admission_number = row.get('admission_number')
        instance.student_class = row.get('class')
        instance.staff_id = row.get('staff_id')
        instance.department = row.get('department')
        instance.position = row.get('position')

        # Set a default password if not provided
        if not instance.password:
            instance.set_password('defaultpassword123')


class TuitionFeeResource(resources.ModelResource):
    """Resource for importing/exporting Tuition Fees"""

    student = fields.Field(
        column_name='student_username',
        attribute='student',
        widget=ForeignKeyWidget(StudentProfile, 'user__username')
    )

    student_name = fields.Field(
        column_name='student_name',
        attribute='student__user__first_name',
        readonly=True
    )

    student_admission = fields.Field(
        column_name='admission_number',
        attribute='student__admission_number',
        readonly=True
    )

    class Meta:
        model = TuitionFee
        fields = (
            'id', 'student', 'student_name', 'student_admission',
            'session', 'term', 'amount_due', 'amount_paid',
            'status', 'due_date', 'paid_date'
        )
        export_order = fields
        import_id_fields = ('student', 'session', 'term')

    def dehydrate_student_name(self, tuition_fee):
        """Export student full name"""
        return tuition_fee.student.user.get_full_name()


class PayrollResource(resources.ModelResource):
    """Resource for importing/exporting Payroll"""

    staff = fields.Field(
        column_name='staff_username',
        attribute='staff',
        widget=ForeignKeyWidget(StaffProfile, 'user__username')
    )

    staff_name = fields.Field(
        column_name='staff_name',
        attribute='staff__user__first_name',
        readonly=True
    )

    staff_id_field = fields.Field(
        column_name='staff_id',
        attribute='staff__staff_id',
        readonly=True
    )

    class Meta:
        model = Payroll
        fields = (
            'id', 'staff', 'staff_name', 'staff_id_field',
            'month', 'year', 'amount', 'paid', 'paid_date'
        )
        export_order = fields
        import_id_fields = ('staff', 'month', 'year')

    def dehydrate_staff_name(self, payroll):
        """Export staff full name"""
        return payroll.staff.user.get_full_name()


class PaymentResource(resources.ModelResource):
    """Resource for importing/exporting Payments"""

    tuition_fee = fields.Field(
        column_name='tuition_fee_id',
        attribute='tuition_fee',
        widget=ForeignKeyWidget(TuitionFee, 'id')
    )

    student_name = fields.Field(
        column_name='student_name',
        attribute='tuition_fee__student__user__first_name',
        readonly=True
    )

    class Meta:
        model = Payment
        fields = (
            'id', 'tuition_fee', 'student_name', 'amount',
            'payment_date', 'method', 'receipt_number',
            'reference', 'notes'
        )
        export_order = fields
        import_id_fields = ('receipt_number',)

    def dehydrate_student_name(self, payment):
        """Export student full name"""
        return payment.tuition_fee.student.user.get_full_name()


class ExpenseResource(resources.ModelResource):
    """Resource for importing/exporting Expenses"""

    created_by_username = fields.Field(
        column_name='created_by_username',
        attribute='created_by__username',
        readonly=True
    )

    class Meta:
        model = Expense
        fields = (
            'id', 'description', 'amount', 'date', 'category',
            'receipt_number', 'vendor', 'notes', 'created_by_username'
        )
        export_order = fields
        import_id_fields = ('receipt_number',)

    def dehydrate_created_by_username(self, expense):
        """Export creator username"""
        if expense.created_by:
            return expense.created_by.username
        return None


# Result Management Resources

class AcademicSessionResource(resources.ModelResource):
    """Resource for importing/exporting Academic Sessions"""
    
    class Meta:
        model = AcademicSession
        fields = ('id', 'name', 'start_date', 'end_date', 'is_current')
        export_order = fields
        import_id_fields = ('name',)


class AcademicTermResource(resources.ModelResource):
    """Resource for importing/exporting Academic Terms"""
    
    session = fields.Field(
        column_name='session_name',
        attribute='session',
        widget=ForeignKeyWidget(AcademicSession, 'name')
    )
    
    class Meta:
        model = AcademicTerm
        fields = ('id', 'session', 'name', 'start_date', 'end_date', 'is_current')
        export_order = fields
        import_id_fields = ('session', 'name')


class SubjectResource(resources.ModelResource):
    """Resource for importing/exporting Subjects"""
    
    class Meta:
        model = Subject
        fields = ('id', 'name', 'code', 'subject_type', 'description', 'is_active')
        export_order = fields
        import_id_fields = ('code',)


class StudentResultResource(resources.ModelResource):
    """Resource for importing/exporting Student Results"""
    
    student = fields.Field(
        column_name='student_admission_number',
        attribute='student',
        widget=ForeignKeyWidget(StudentProfile, 'admission_number')
    )
    
    student_name = fields.Field(
        column_name='student_name',
        attribute='student__user__first_name',
        readonly=True
    )
    
    subject = fields.Field(
        column_name='subject_code',
        attribute='subject',
        widget=ForeignKeyWidget(Subject, 'code')
    )
    
    session = fields.Field(
        column_name='session_name',
        attribute='session',
        widget=ForeignKeyWidget(AcademicSession, 'name')
    )
    
    term = fields.Field(
        column_name='term_name',
        attribute='term',
        widget=ForeignKeyWidget(AcademicTerm, 'name')
    )
    
    class Meta:
        model = StudentResult
        fields = (
            'id', 'student', 'student_name', 'subject', 'session', 'term',
            'first_ca', 'second_ca', 'exam_score', 'cbt_score', 
            'total_score', 'grade', 'position'
        )
        export_order = fields
        import_id_fields = ('student', 'subject', 'session', 'term')
        
    def dehydrate_student_name(self, student_result):
        """Export student full name"""
        return student_result.student.user.get_full_name()
    
    def before_import_row(self, row, **kwargs):
        """Process row before importing"""
        # Auto-calculate total if not provided
        if not row.get('total_score'):
            first_ca = float(row.get('first_ca', 0))
            second_ca = float(row.get('second_ca', 0))
            exam_score = float(row.get('exam_score', 0))
            row['total_score'] = first_ca + second_ca + exam_score


class TermResultResource(resources.ModelResource):
    """Resource for importing/exporting Term Results"""
    
    student = fields.Field(
        column_name='student_admission_number',
        attribute='student',
        widget=ForeignKeyWidget(StudentProfile, 'admission_number')
    )
    
    student_name = fields.Field(
        column_name='student_name',
        attribute='student__user__first_name',
        readonly=True
    )
    
    session = fields.Field(
        column_name='session_name',
        attribute='session',
        widget=ForeignKeyWidget(AcademicSession, 'name')
    )
    
    term = fields.Field(
        column_name='term_name',
        attribute='term',
        widget=ForeignKeyWidget(AcademicTerm, 'name')
    )
    
    class Meta:
        model = TermResult
        fields = (
            'id', 'student', 'student_name', 'session', 'term',
            'total_subjects', 'subjects_passed', 'subjects_failed',
            'total_obtainable', 'total_obtained', 'percentage', 'gpa',
            'class_position', 'total_students_in_class',
            'class_teacher_comment', 'principal_comment',
            'punctuality', 'attentiveness', 'neatness', 'politeness',
            'is_published'
        )
        export_order = fields
        import_id_fields = ('student', 'session', 'term')
        
    def dehydrate_student_name(self, term_result):
        """Export student full name"""
        return term_result.student.user.get_full_name()


class CBTExamResource(resources.ModelResource):
    """Resource for importing/exporting CBT Exams"""
    
    subject = fields.Field(
        column_name='subject_code',
        attribute='subject',
        widget=ForeignKeyWidget('academics.Subject', 'code')
    )
    
    session = fields.Field(
        column_name='session_name',
        attribute='session',
        widget=ForeignKeyWidget('academics.AcademicSession', 'name')
    )
    
    term = fields.Field(
        column_name='term_name',
        attribute='term',
        widget=ForeignKeyWidget('academics.AcademicTerm', 'name')
    )
    
    class Meta:
        model = CBTExam
        fields = (
            'id', 'title', 'subject', 'assigned_class', 'session', 'term',
            'start_time', 'end_time', 'duration_minutes', 'total_marks',
            'pass_mark', 'instructions', 'is_active'
        )
        export_order = fields
        import_id_fields = ('title', 'subject', 'assigned_class')


class CBTSessionResource(resources.ModelResource):
    """Resource for importing/exporting CBT Sessions"""
    
    student = fields.Field(
        column_name='student_admission_number',
        attribute='student',
        widget=ForeignKeyWidget(StudentProfile, 'admission_number')
    )
    
    exam_title = fields.Field(
        column_name='exam_title',
        attribute='exam__title',
        readonly=True
    )
    
    student_name = fields.Field(
        column_name='student_name',
        readonly=True
    )
    
    subject_name = fields.Field(
        column_name='subject_name',
        attribute='exam__subject__name',
        readonly=True
    )
    
    class_name = fields.Field(
        column_name='class_name',
        attribute='exam__assigned_class',
        readonly=True
    )
    
    class Meta:
        model = CBTSession
        fields = (
            'id', 'exam_title', 'subject_name', 'class_name', 'student', 
            'student_name', 'started_at', 'completed_at', 'score', 
            'percentage', 'time_taken', 'is_submitted'
        )
        export_order = fields
        
    def dehydrate_student_name(self, cbt_session):
        return cbt_session.student.user.get_full_name()
