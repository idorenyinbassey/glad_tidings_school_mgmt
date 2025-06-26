from django.conf import settings
from django.db import models

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=30, unique=True)
    date_of_birth = models.DateField()
    address = models.TextField(blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_contact = models.CharField(max_length=30, blank=True)
    # Add more fields as needed

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
