from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.db import models
from academics.models import Announcement
from core.models import UserNotification

@login_required
def notifications(request):
    """Display all notifications and announcements for the user"""
    # Get announcements - cache the query for 10 minutes (since announcements don't change often)
    from django.core.cache import cache
    from django.utils import timezone
    import hashlib
    
    # Create a cache key based on the user and role
    user_role = getattr(request.user, 'role', 'anonymous')
    cache_key = f"announcements_list_{request.user.id}_{user_role}"
    announcements = cache.get(cache_key)
    
    if not announcements:
        # Get announcements with optimized query - filter by role and active status
        now = timezone.now()
        
        # Build the audience filter based on user role
        audience_filter = ['all']
        if user_role:
            if user_role == 'student':
                audience_filter.append('students')
            elif user_role == 'staff':
                audience_filter.append('staff')
            elif user_role == 'admin':
                audience_filter.append('admin')
                audience_filter.append('staff')  # Admins can see staff announcements too
            elif user_role == 'it_support':
                audience_filter.append('staff')  # IT support can see staff announcements
        
        # Build the complete query with publish/expiry date filtering
        announcements = Announcement.objects.filter(
            is_active=True,
            audience__in=audience_filter
        ).filter(
            # Either publish_date is null or it's in the past
            models.Q(publish_date__isnull=True) | models.Q(publish_date__lte=now)
        ).filter(
            # Either expiry_date is null or it's in the future
            models.Q(expiry_date__isnull=True) | models.Q(expiry_date__gt=now)
        ).select_related('created_by').order_by('-priority', '-created_at')[:15]
        
        # Cache for 10 minutes
        cache.set(cache_key, announcements, 600)
    
    # Get user-specific notifications with optimized query that uses our compound index
    user_notifications = UserNotification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:20]
    
    # If mark_all_read parameter is present, mark all as read
    if request.GET.get('mark_all_read'):
        UserNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return redirect('notifications')
    
    return render(request, 'core/notifications.html', {
        'announcements': announcements,
        'user_notifications': user_notifications
    })

@login_required
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    try:
        notification = UserNotification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        # If there's a link, redirect to it
        if notification.link:
            return redirect(notification.link)
        
        # Otherwise redirect to notifications page
        return redirect('notifications')
    except UserNotification.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False}, status=404)
        
        return redirect('notifications')

def get_unread_count(request):
    """Return the number of unread notifications for the current user"""
    if not request.user.is_authenticated:
        return JsonResponse({'count': 0})
    
    count = UserNotification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})
