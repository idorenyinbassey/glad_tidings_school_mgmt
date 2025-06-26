from django.contrib import admin
from .models import CBTExam, CBTQuestion, CBTSession, CBTAnswer

class CBTQuestionInline(admin.TabularInline):
    model = CBTQuestion
    extra = 1

@admin.register(CBTExam)
class CBTExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'assigned_class', 'start_time', 'end_time', 'created_by')
    inlines = [CBTQuestionInline]
    search_fields = ('title', 'subject', 'assigned_class')

@admin.register(CBTSession)
class CBTSessionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student', 'started_at', 'completed_at', 'score')
    search_fields = ('exam__title', 'student__admission_number')

@admin.register(CBTAnswer)
class CBTAnswerAdmin(admin.ModelAdmin):
    list_display = ('session', 'question', 'selected_option', 'is_correct')
    search_fields = ('session__exam__title', 'question__question_text')
