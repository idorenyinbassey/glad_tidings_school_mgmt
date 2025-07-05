from django.conf import settings
from django.db import models

class ClassTimetable(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    class_name = models.CharField(max_length=50)
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    period = models.CharField(max_length=20)
    subject = models.CharField(max_length=100)
    teacher = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='classtimetable_created')

    class Meta:
        unique_together = ('class_name', 'day_of_week', 'period')
        indexes = [
            models.Index(fields=['class_name', 'day_of_week']),
        ]
        
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")
            
    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.class_name} - {self.day_of_week.capitalize()} {self.period}"

class ELibraryResource(models.Model):
    RESOURCE_TYPES = [
        ('book', 'Book'),
        ('article', 'Article'),
        ('worksheet', 'Worksheet'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('presentation', 'Presentation'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='other')
    subject = models.CharField(max_length=100, blank=True)
    grade_level = models.CharField(max_length=50, blank=True, help_text="Grade/Class level this resource is intended for")
    file = models.FileField(upload_to='elibrary/')
    file_size = models.PositiveIntegerField(editable=False, null=True, help_text="File size in bytes")
    thumbnail = models.ImageField(upload_to='elibrary/thumbnails/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='elibrary_uploaded')
    download_count = models.PositiveIntegerField(default=0, editable=False)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['resource_type', '-uploaded_at']),
            models.Index(fields=['subject', 'grade_level']),
        ]

    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        if self.file and hasattr(self.file, 'size'):
            self.file_size = self.file.size
        super().save(*args, **kwargs)
        
    def get_file_size_display(self):
        if not self.file_size:
            return "Unknown"
            
        size_bytes = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024 or unit == 'GB':
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024

class SchoolCalendarEvent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='calendar_created')

    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"

class Announcement(models.Model):
    AUDIENCE_CHOICES = [
        ('all', 'Everyone'),
        ('students', 'Students Only'), 
        ('staff', 'Staff Only'),
        ('admin', 'Administrators Only'),
        ('parents', 'Parents Only'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Normal'),
        (3, 'High'),
        (4, 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    audience = models.CharField(max_length=10, choices=AUDIENCE_CHOICES, default='all')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='announcement_created')
    is_active = models.BooleanField(default=True)
    publish_date = models.DateTimeField(null=True, blank=True, help_text="When this announcement should become visible")
    expiry_date = models.DateTimeField(null=True, blank=True, help_text="When this announcement should no longer be visible")
    
    class Meta:
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['audience', 'is_active', '-created_at']),
            models.Index(fields=['priority', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_audience_display()})"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False
    
    @property
    def is_published(self):
        from django.utils import timezone
        if self.publish_date:
            return timezone.now() >= self.publish_date
        return True
