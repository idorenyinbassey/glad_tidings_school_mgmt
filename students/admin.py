from django.contrib import admin
from .models import StudentProfile, AcademicStatus, AttendanceRecord

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'admission_number', 'date_of_birth', 'guardian_name')
    search_fields = ('user__username', 'admission_number', 'guardian_name')

@admin.register(AcademicStatus)
class AcademicStatusAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'term', 'current_class', 'promoted')
    search_fields = ('student__admission_number', 'session', 'term', 'current_class')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'present')
    search_fields = ('student__admission_number', 'date')
