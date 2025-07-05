from django.contrib import admin
from .models import (
    AcademicSession, AcademicTerm, Subject, StudentClass, Assessment,
    StudentResult, TermResult, ResultSheet
)


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current', 'created_at')
    list_filter = ('is_current', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ('session', 'name', 'start_date', 'end_date', 'is_current', 'created_at')
    list_filter = ('session', 'name', 'is_current', 'created_at')
    search_fields = ('session__name', 'name')
    readonly_fields = ('created_at',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'is_active', 'created_at')
    list_filter = ('department', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'department')
    readonly_fields = ('created_at',)
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'class_teacher', 'is_active', 'created_at')
    list_filter = ('level', 'is_active', 'created_at')
    search_fields = ('name', 'level')
    filter_horizontal = ('subjects',)
    readonly_fields = ('created_at',)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'max_score', 'weight_percentage', 'is_active', 'created_at')
    list_filter = ('type', 'is_active', 'created_at')
    search_fields = ('name', 'type')
    readonly_fields = ('created_at',)


@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'assessment', 'score', 'percentage',
                    'session', 'term', 'entered_by', 'entered_at')
    list_filter = ('session', 'term', 'subject', 'assessment', 'student_class', 'entered_at')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'subject__name', 'assessment__name')
    readonly_fields = ('entered_at', 'updated_at', 'percentage')
    
    def percentage(self, obj):
        return f"{obj.percentage:.1f}%"
    percentage.short_description = 'Percentage'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.entered_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TermResult)
class TermResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'session', 'term', 'percentage', 'grade', 'position_in_class', 'compiled_at')
    list_filter = ('session', 'term', 'subject', 'grade', 'student_class')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'subject__name')
    readonly_fields = ('compiled_at',)
    
    def save_model(self, request, obj, form, change):
        obj.compiled_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ResultSheet)
class ResultSheetAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'term', 'overall_percentage', 'overall_grade',
                    'position_in_class', 'is_published', 'created_at')
    list_filter = ('session', 'term', 'overall_grade', 'is_published', 'student_class', 'created_at')
    search_fields = ('student__user__first_name', 'student__user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    
    actions = ['publish_results', 'unpublish_results']
    
    def publish_results(self, request, queryset):
        for result_sheet in queryset:
            result_sheet.publish(request.user)
        self.message_user(request, f"Successfully published {queryset.count()} result sheets.")
    publish_results.short_description = "Publish selected result sheets"
    
    def unpublish_results(self, request, queryset):
        queryset.update(is_published=False, published_at=None, published_by=None)
        self.message_user(request, f"Successfully unpublished {queryset.count()} result sheets.")
    unpublish_results.short_description = "Unpublish selected result sheets"
