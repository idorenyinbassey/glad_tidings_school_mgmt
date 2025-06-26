from django.contrib import admin
from .models import Assignment, Submission

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'assigned_class', 'due_date', 'created_by')
    search_fields = ('title', 'subject', 'assigned_class')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'grade', 'graded_by', 'graded_at')
    search_fields = ('assignment__title', 'student__admission_number', 'grade')
