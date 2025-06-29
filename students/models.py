from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=30, unique=True)
    date_of_birth = models.DateField()
    address = models.TextField(blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_contact = models.CharField(max_length=30, blank=True)
    # Add more fields as needed

    def clean(self):
        """Validate the model fields"""
        super().clean()
        
        # Validate date of birth
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError("Date of birth cannot be in the future")
        
        # Validate age (student should be between 3 and 25 years old)
        if self.date_of_birth:
            age = (timezone.now().date() - self.date_of_birth).days // 365
            if age < 3 or age > 25:
                raise ValidationError("Student age must be between 3 and 25 years")
        
        # Validate admission number format (should be alphanumeric)
        if self.admission_number and not self.admission_number.replace('-', '').replace('/', '').isalnum():
            raise ValidationError("Admission number should contain only letters, numbers, hyphens, and slashes")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.admission_number})"

class AcademicStatus(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='academic_statuses')
    session = models.CharField(max_length=20)
    term = models.CharField(max_length=20)
    current_class = models.CharField(max_length=50)
    promoted = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    # Add more fields as needed

    def __str__(self):
        return f"{self.student} - {self.session} {self.term}"

class AttendanceRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    present = models.BooleanField(default=True)
    # Add more fields as needed

    def __str__(self):
        return f"{self.student} - {self.date} - {'Present' if self.present else 'Absent'}"
