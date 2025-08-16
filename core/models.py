from django.db import models
from django.conf import settings
from academics.models import Announcement
from django.utils import timezone

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


class InboxMessage(models.Model):
    """Unified inbox for site submissions (Admission applications and Contact messages)."""
    MESSAGE_TYPES = (
        ('admission', 'Admission Application'),
        ('contact', 'Contact Message'),
    )
    STATUS_CHOICES = (
        ('new', 'New'),
        ('read', 'Read'),
        ('processed', 'Processed'),
    )

    # General
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', db_index=True)
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='inbox_submissions'
    )

    # Common contact info
    full_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    # Contact message fields
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True)

    # Admission application fields
    application_type = models.CharField(max_length=20, blank=True)
    academic_year = models.CharField(max_length=20, blank=True)
    grade_level = models.CharField(max_length=20, blank=True)

    first_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)

    parent_name = models.CharField(max_length=150, blank=True)
    relationship = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    previous_school = models.CharField(max_length=200, blank=True)
    agree_terms = models.BooleanField(default=False)

    # Metadata
    source_page = models.CharField(max_length=100, blank=True)
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Inbox'
        verbose_name_plural = 'Inbox'
        indexes = [
            models.Index(fields=['message_type', 'status', '-submitted_at']),
        ]

    def __str__(self):
        base = dict(self.MESSAGE_TYPES).get(self.message_type, self.message_type)
        if self.message_type == 'admission':
            name = f"{self.first_name} {self.last_name}".strip()
            return f"{base} - {name or 'Unknown'} ({self.submitted_at.date()})"
        return f"{base} - {self.subject or self.full_name or 'No subject'} ({self.submitted_at.date()})"


class NewsPost(models.Model):
    """Simple CMS for latest news/updates shown on landing page."""
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class UpcomingEvent(models.Model):
    """CMS for upcoming events shown on landing page side panel."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return self.title
