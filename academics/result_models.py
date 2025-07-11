from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from students.models import StudentProfile
from staff.models import StaffProfile


class AcademicSession(models.Model):
    """Academic year/session (e.g., 2024/2025)"""
    name = models.CharField(max_length=20, unique=True, help_text="e.g., 2024/2025")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-start_date']

    def save(self, *args, **kwargs):
        if self.is_current:
            # Ensure only one session is current
            AcademicSession.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AcademicTerm(models.Model):
    """Academic terms within a session"""
    TERM_CHOICES = [
        ('first', 'First Term'),
        ('second', 'Second Term'),
        ('third', 'Third Term'),
    ]
    
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='terms')
    name = models.CharField(max_length=10, choices=TERM_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'name')
        ordering = ['session', 'name']

    def save(self, *args, **kwargs):
        if self.is_current:
            # Ensure only one term is current per session
            AcademicTerm.objects.filter(session=self.session, is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.session.name} - {self.get_name_display()}"


class Subject(models.Model):
    """Subjects taught in the school"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="e.g., MATH101")
    department = models.CharField(max_length=50, help_text="e.g., Science, Arts")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class StudentClass(models.Model):
    """Student classes/grades"""
    name = models.CharField(max_length=50, unique=True, help_text="e.g., Grade 10A, JSS 1B")
    level = models.CharField(max_length=20, help_text="e.g., JSS1, SS2")
    subjects = models.ManyToManyField(Subject, related_name='classes')
    class_teacher = models.ForeignKey(
        StaffProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='classes_taught'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Student Classes"

    def __str__(self):
        return self.name


class Assessment(models.Model):
    """Different types of assessments"""
    ASSESSMENT_TYPES = [
        ('ca1', 'First CA (Continuous Assessment)'),
        ('ca2', 'Second CA (Continuous Assessment)'),
        ('ca3', 'Third CA (Continuous Assessment)'),
        ('exam', 'Examination'),
        ('assignment', 'Assignment'),
        ('project', 'Project'),
        ('practical', 'Practical'),
    ]
    
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    max_score = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    weight_percentage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Weight in final grade calculation"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['type', 'name']

    def __str__(self):
        return f"{self.name} ({self.max_score} marks)"


class StudentResult(models.Model):
    """Individual student results for specific assessments"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    
    score = models.FloatField(validators=[MinValueValidator(0)])
    remarks = models.TextField(blank=True)
    
    # Tracking fields
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    entered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'subject', 'session', 'term', 'assessment')
        ordering = ['-session', '-term', 'student__user__last_name', 'subject']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.score > self.assessment.max_score:
            raise ValidationError(f"Score cannot exceed {self.assessment.max_score}")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def percentage(self):
        return (self.score / self.assessment.max_score) * 100

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.name} - {self.assessment.name}: {self.score}"


class TermResult(models.Model):
    """Compiled results for a student in a term"""
    GRADE_CHOICES = [
        ('A', 'A (Excellent)'),
        ('B', 'B (Very Good)'),
        ('C', 'C (Good)'),
        ('D', 'D (Pass)'),
        ('F', 'F (Fail)'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='term_results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    
    # Calculated fields
    total_score = models.FloatField(default=0)
    total_possible = models.FloatField(default=100)
    percentage = models.FloatField(default=0)
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES, blank=True)
    
    # Position in class
    position_in_class = models.PositiveIntegerField(null=True, blank=True)
    total_students = models.PositiveIntegerField(null=True, blank=True)
    
    # Teacher's remarks
    teacher_remarks = models.TextField(blank=True)
    
    # Tracking
    compiled_at = models.DateTimeField(auto_now=True)
    compiled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = ('student', 'subject', 'session', 'term')
        ordering = ['-session', '-term', '-percentage']

    def calculate_grade(self):
        """Calculate grade based on percentage"""
        if self.percentage >= 80:
            return 'A'
        elif self.percentage >= 70:
            return 'B'
        elif self.percentage >= 60:
            return 'C'
        elif self.percentage >= 45:
            return 'D'
        else:
            return 'F'

    def compile_result(self):
        """Compile result from individual assessments"""
        assessments = StudentResult.objects.filter(
            student=self.student,
            subject=self.subject,
            session=self.session,
            term=self.term
        )
        
        total_weighted_score = 0
        total_weight = 0
        
        for result in assessments:
            weighted_score = (result.score / result.assessment.max_score) * result.assessment.weight_percentage
            total_weighted_score += weighted_score
            total_weight += result.assessment.weight_percentage
        
        if total_weight > 0:
            self.percentage = total_weighted_score
            self.total_score = (self.percentage / 100) * self.total_possible
            self.grade = self.calculate_grade()
        
        self.save()

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.name} - {self.term}: {self.percentage}%"


class ResultSheet(models.Model):
    """Complete result sheet for a student in a term"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='result_sheets')
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    
    # Overall performance
    total_score = models.FloatField(default=0)
    total_possible = models.FloatField(default=0)
    overall_percentage = models.FloatField(default=0)
    overall_grade = models.CharField(max_length=1, choices=TermResult.GRADE_CHOICES, blank=True)
    
    # Position
    position_in_class = models.PositiveIntegerField(null=True, blank=True)
    total_students = models.PositiveIntegerField(null=True, blank=True)
    
    # Attendance
    total_days_present = models.PositiveIntegerField(default=0)
    total_days_absent = models.PositiveIntegerField(default=0)
    total_school_days = models.PositiveIntegerField(default=0)
    
    # Comments
    class_teacher_remarks = models.TextField(blank=True)
    principal_remarks = models.TextField(blank=True)
    
    # Status
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='published_results'
    )
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'session', 'term')
        ordering = ['-session', '-term', '-overall_percentage']

    def compile_result_sheet(self):
        """Compile the complete result sheet"""
        term_results = TermResult.objects.filter(
            student=self.student,
            session=self.session,
            term=self.term
        )
        
        self.total_score = sum(tr.total_score for tr in term_results)
        self.total_possible = sum(tr.total_possible for tr in term_results)
        
        if self.total_possible > 0:
            self.overall_percentage = (self.total_score / self.total_possible) * 100
            self.overall_grade = self.calculate_overall_grade()
        
        self.save()

    def calculate_overall_grade(self):
        """Calculate overall grade"""
        if self.overall_percentage >= 80:
            return 'A'
        elif self.overall_percentage >= 70:
            return 'B'
        elif self.overall_percentage >= 60:
            return 'C'
        elif self.overall_percentage >= 45:
            return 'D'
        else:
            return 'F'

    def publish(self, user):
        """Publish the result sheet"""
        self.is_published = True
        self.published_at = timezone.now()
        self.published_by = user
        self.save()

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.session.name} {self.term.get_name_display()}"
