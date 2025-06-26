from django.conf import settings
from django.db import models
from django.utils import timezone

class StaffProfile(models.Model):
    POSITION_CHOICES = [
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
        ('accountant', 'Accountant'),
        ('it_support', 'IT Support'),
        ('other', 'Other'),
    ]
    DEPARTMENT_CHOICES = [
        ('science', 'Science'),
        ('arts', 'Arts'),
        ('admin', 'Administration'),
        ('accounts', 'Accounts'),
        ('it', 'IT'),
        ('other', 'Other'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile')
    staff_id = models.CharField(max_length=30, unique=True)
    position = models.CharField(max_length=100, choices=POSITION_CHOICES)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='staffprofile_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='staffprofile_updated')

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.staff_id})"

class TeacherTimetable(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='timetables')
    day_of_week = models.CharField(max_length=10)
    period = models.CharField(max_length=20)
    assigned_class = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='timetable_created')

    class Meta:
        unique_together = ('staff', 'day_of_week', 'period')

    def __str__(self):
        return f"{self.staff} - {self.day_of_week} {self.period} - {self.assigned_class}"

class StudentPerformance(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='performances')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='performances')
    subject = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='performance_created')

    def __str__(self):
        return f"{self.student} - {self.subject} by {self.staff}"

class StaffNotice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='notice_created')
    recipients = models.ManyToManyField(StaffProfile, related_name='notices')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class StaffAttendance(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    present = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='attendance_created')

    class Meta:
        unique_together = ('staff', 'date')

    def __str__(self):
        return f"{self.staff} - {self.date} - {'Present' if self.present else 'Absent'}"
