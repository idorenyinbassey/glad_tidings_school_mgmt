from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from .models import CBTExam, CBTQuestion, CBTSession, CBTAnswer


# Import/Export Resources for CBT
class CBTExamResource(resources.ModelResource):
    class Meta:
        model = CBTExam
        fields = (
            'id', 'title', 'subject', 'assigned_class',
            'start_time', 'end_time', 'duration_minutes', 'total_marks',
            'pass_mark', 'instructions', 'is_active'
        )
        import_id_fields = ('title', 'subject', 'assigned_class')


class CBTSessionResource(resources.ModelResource):
    student_name = fields.Field(
        column_name='student_name',
        readonly=True
    )
    exam_title = fields.Field(
        column_name='exam_title',
        attribute='exam__title',
        readonly=True
    )
    
    class Meta:
        model = CBTSession
        fields = (
            'id', 'exam_title', 'student', 'student_name', 'started_at',
            'completed_at', 'score', 'percentage', 'is_submitted'
        )
        export_order = fields
        
    def dehydrate_student_name(self, cbt_session):
        return cbt_session.student.user.get_full_name()


class CBTQuestionInline(admin.TabularInline):
    model = CBTQuestion
    extra = 1
    fields = ('question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'marks')


@admin.register(CBTExam)
class CBTExamAdmin(ImportExportModelAdmin):
    resource_class = CBTExamResource
    list_display = (
        'title', 'subject', 'assigned_class',
        'start_time', 'end_time', 'total_questions', 'total_sessions_count',
        'is_active'
    )
    list_filter = ('subject', 'assigned_class', 'is_active')
    search_fields = ('title', 'subject', 'assigned_class')
    inlines = [CBTQuestionInline]
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subject', 'assigned_class')
        }),
        ('Exam Settings', {
            'fields': ('start_time', 'end_time', 'duration_minutes', 'total_marks', 'pass_mark')
        }),
        ('Instructions & Status', {
            'fields': ('instructions', 'is_active')
        }),
        ('System Info', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def total_questions(self, obj):
        return obj.questions.count()
    total_questions.short_description = 'Questions'
    
    def total_sessions_count(self, obj):
        total = obj.sessions.count()
        completed = obj.sessions.filter(is_submitted=True).count()
        return format_html(
            '<span style="color: blue;">{}</span> / <span style="color: green;">{}</span>',
            total, completed
        )
    total_sessions_count.short_description = 'Sessions (Total/Completed)'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CBTSession)
class CBTSessionAdmin(ImportExportModelAdmin):
    resource_class = CBTSessionResource
    list_display = (
        'exam_title', 'student_name', 'started_at', 'completion_status',
        'score_display', 'percentage_display', 'grade_display'
    )
    list_filter = ('exam__subject', 'is_submitted', 'exam__assigned_class')
    search_fields = (
        'exam__title', 'student__user__first_name', 'student__user__last_name',
        'student__admission_number'
    )
    readonly_fields = ('started_at', 'score', 'percentage')
    
    def exam_title(self, obj):
        return obj.exam.title
    exam_title.short_description = 'Exam'
    exam_title.admin_order_field = 'exam__title'
    
    def student_name(self, obj):
        return obj.student.user.get_full_name()
    student_name.short_description = 'Student'
    student_name.admin_order_field = 'student__user__last_name'
    
    def completion_status(self, obj):
        if obj.is_submitted:
            return format_html('<span style="color: green;">✓ Completed</span>')
        else:
            return format_html('<span style="color: orange;">⏳ In Progress</span>')
    completion_status.short_description = 'Status'
    
    def score_display(self, obj):
        if obj.score is not None:
            if obj.is_passed:
                color = 'green'
            else:
                color = 'red'
            return format_html('<span style="color: {}; font-weight: bold;">{}</span>',
                               color, f'{obj.score:.2f}')
        return '-'
    score_display.short_description = 'Score'
    
    def percentage_display(self, obj):
        if obj.percentage is not None:
            if obj.percentage >= 70:
                color = 'green'
            elif obj.percentage >= 50:
                color = 'orange'
            else:
                color = 'red'
            return format_html('<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
                               color, obj.percentage)
        return '-'
    percentage_display.short_description = 'Percentage'
    
    def grade_display(self, obj):
        grade = obj.grade
        grade_colors = {
            'A+': '#2e7d32', 'A': '#388e3c', 'B+': '#689f38', 'B': '#7cb342',
            'C+': '#fbc02d', 'C': '#ff9800', 'D+': '#ff5722', 'D': '#d32f2f',
            'E': '#c62828', 'F': '#b71c1c'
        }
        color = grade_colors.get(grade, '#757575')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>',
                           color, grade)
    grade_display.short_description = 'Grade'


@admin.register(CBTQuestion)
class CBTQuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'question_text_short', 'correct_option', 'marks')
    list_filter = ('exam__subject', 'correct_option')
    search_fields = ('exam__title', 'question_text')
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question'


@admin.register(CBTAnswer)
class CBTAnswerAdmin(admin.ModelAdmin):
    list_display = ('session', 'question_short', 'selected_option', 'correct_status', 'answered_at')
    list_filter = ('is_correct', 'selected_option', 'session__exam__subject')
    search_fields = ('session__exam__title', 'question__question_text', 'session__student__user__first_name')
    
    def question_short(self, obj):
        return obj.question.question_text[:30] + "..."
    question_short.short_description = 'Question'
    
    def correct_status(self, obj):
        if obj.is_correct:
            return format_html('<span style="color: green;">✓ Correct</span>')
        else:
            return format_html('<span style="color: red;">✗ Wrong</span>')
    correct_status.short_description = 'Status'
