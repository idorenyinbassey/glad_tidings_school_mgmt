from django.db.models.signals import post_save
from django.dispatch import receiver
from academics.models import Announcement
from .models import UserNotification, NewsPost, UpcomingEvent

@receiver(post_save, sender=Announcement)
def create_notifications_from_announcement(sender, instance, created, **kwargs):
    """When a new announcement is created, create notifications for all users"""
    if created and instance.is_active:
        UserNotification.create_from_announcement(instance)


@receiver(post_save, sender=NewsPost)
def news_post_notification(sender, instance, created, **kwargs):
    """Create an Announcement on new NewsPost to leverage existing notification system."""
    if created and instance.is_published:
        Announcement.objects.create(
            title=f"News: {instance.title}",
            message=(instance.summary or instance.content[:200] + '...'),
            audience='all',
            priority=2,
            is_active=True,
            created_by=instance.created_by,
        )


@receiver(post_save, sender=UpcomingEvent)
def event_notification(sender, instance, created, **kwargs):
    if created and instance.is_published:
        date_str = instance.start_time.strftime('%b %d, %Y %I:%M %p')
        Announcement.objects.create(
            title=f"Upcoming Event: {instance.title}",
            message=f"Starts {date_str} at {instance.location}. { (instance.description or '')[:160] }",
            audience='all',
            priority=3,
            is_active=True,
            created_by=instance.created_by,
        )
