from django.db import models
from django.conf import settings
from academics.models import Announcement

class UserNotification(models.Model):
    """Model for user-specific notifications that can be marked as read"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', db_index=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True, help_text="Optional link to redirect when clicked")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Compound index for common query pattern: user + is_read + created_at
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    @classmethod
    def create_from_announcement(cls, announcement):
        """Create notifications for all users from an announcement"""
        from users.models import CustomUser
        # Get all users
        users = CustomUser.objects.all()
        
        # Create a notification for each user
        notifications = []
        for user in users:
            notification = cls(
                user=user,
                title=announcement.title,
                message=announcement.message,
                # Link to the notifications page
                link='/notifications/'
            )
            notifications.append(notification)
        
        # Bulk create all notifications
        cls.objects.bulk_create(notifications)
        return notifications
