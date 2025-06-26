from django.contrib import admin
from .models import StaffProfile, TeacherTimetable, StudentPerformance

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'staff_id', 'position', 'department')
    search_fields = ('user__username', 'staff_id', 'position', 'department')

@admin.register(TeacherTimetable)
class TeacherTimetableAdmin(admin.ModelAdmin):
    list_display = ('staff', 'day_of_week', 'period', 'assigned_class', 'subject')
    search_fields = ('staff__staff_id', 'assigned_class', 'subject')

@admin.register(StudentPerformance)
class StudentPerformanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'score', 'staff')
    search_fields = ('student__admission_number', 'subject', 'staff__staff_id')
