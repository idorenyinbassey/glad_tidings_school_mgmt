from django.db.models.signals import post_save
from django.dispatch import receiver
from academics.models import Announcement
from .models import UserNotification

@receiver(post_save, sender=Announcement)
def create_notifications_from_announcement(sender, instance, created, **kwargs):
    """When a new announcement is created, create notifications for all users"""
    if created and instance.is_active:
        UserNotification.create_from_announcement(instance)
