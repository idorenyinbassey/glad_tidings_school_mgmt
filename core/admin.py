from django.contrib import admin
from .models import UserNotification

@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
