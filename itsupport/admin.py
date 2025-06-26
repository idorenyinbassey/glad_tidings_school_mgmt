from django.contrib import admin
from .models import SystemHealthLog, TroubleshootingLog, UserAccessRequest, BugReport

@admin.register(SystemHealthLog)
class SystemHealthLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'status', 'message', 'created_by')
    search_fields = ('status', 'message')

@admin.register(TroubleshootingLog)
class TroubleshootingLogAdmin(admin.ModelAdmin):
    list_display = ('description', 'reported_by', 'created_at', 'resolved', 'resolved_at', 'resolved_by')
    search_fields = ('description', 'reported_by__username')
    list_filter = ('resolved',)

@admin.register(UserAccessRequest)
class UserAccessRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'request_type', 'status', 'created_at', 'processed_at', 'processed_by')
    search_fields = ('user__username', 'request_type', 'status')
    list_filter = ('status', 'request_type')

@admin.register(BugReport)
class BugReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'reported_by', 'created_at', 'resolved', 'resolved_at', 'resolved_by')
    search_fields = ('title', 'description', 'reported_by__username')
    list_filter = ('resolved',)
