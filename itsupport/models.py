from django.conf import settings
from django.db import models

class SystemHealthLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100)
    message = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='systemhealth_created')

    def __str__(self):
        return f"{self.timestamp} - {self.status}"

class TroubleshootingLog(models.Model):
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='troubleshooting_reported')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='troubleshooting_resolved')
    resolution_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.description[:30]}... - {'Resolved' if self.resolved else 'Open'}"

class UserAccessRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='access_requests')
    request_type = models.CharField(max_length=50, choices=[('create', 'Create'), ('suspend', 'Suspend'), ('reset', 'Reset Password'), ('other', 'Other')])
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='access_processed')

    def __str__(self):
        return f"{self.user} - {self.request_type} - {self.status}"

class BugReport(models.Model):
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='bugreport_reported')
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='bugreport_resolved')
    resolution_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {'Resolved' if self.resolved else 'Open'}"
