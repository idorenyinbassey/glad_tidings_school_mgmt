from django.contrib import admin
from .models import UserNotification, InboxMessage, NewsPost, UpcomingEvent

@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(InboxMessage)
class InboxMessageAdmin(admin.ModelAdmin):
    list_display = (
        'message_type', 'status', 'submitted_at', 'full_name', 'email', 'phone',
        'subject', 'application_type', 'academic_year', 'grade_level'
    )
    list_filter = ('message_type', 'status', 'submitted_at', 'academic_year', 'grade_level')
    search_fields = (
        'full_name', 'email', 'phone', 'subject', 'message',
        'first_name', 'last_name', 'parent_name', 'previous_school'
    )
    date_hierarchy = 'submitted_at'
    readonly_fields = ('submitted_at', 'updated_at', 'source_ip', 'user_agent', 'submitted_by')
    fieldsets = (
        ('Meta', {
            'fields': ('message_type', 'status', 'submitted_at', 'updated_at', 'submitted_by', 'source_page', 'source_ip', 'user_agent')
        }),
        ('Contact Details', {
            'fields': ('full_name', 'email', 'phone', 'subject', 'message')
        }),
        ('Admission Details', {
            'fields': (
                'application_type', 'academic_year', 'grade_level',
                'first_name', 'middle_name', 'last_name', 'dob', 'gender',
                'parent_name', 'relationship', 'address', 'previous_school', 'agree_terms'
            )
        }),
    )


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'published_at', 'created_by')
    list_filter = ('is_published', 'published_at')
    search_fields = ('title', 'summary', 'content')
    date_hierarchy = 'published_at'
    actions = ['publish_posts']
    class Media:
        js = (
            'https://cdn.jsdelivr.net/npm/tinymce@6.8.3/tinymce.min.js',
            'admin/js/tinymce_init.js',
        )

    def publish_posts(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"Published {updated} post(s)")


@admin.register(UpcomingEvent)
class UpcomingEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'start_time'
    class Media:
        js = (
            'https://cdn.jsdelivr.net/npm/tinymce@6.8.3/tinymce.min.js',
            'admin/js/tinymce_init.js',
        )
