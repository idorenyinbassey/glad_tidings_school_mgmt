from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import UserNotification
from .serializers import UserNotificationSerializer


class UserNotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notifications via API
    """
    serializer_class = UserNotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_read']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return notifications for the current user only"""
        return UserNotification.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user when creating a notification"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a specific notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read for the current user"""
        updated_count = UserNotification.objects.filter(
            user=request.user, 
            is_read=False
        ).update(is_read=True)
        
        return Response({
            'status': 'all notifications marked as read',
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get the count of unread notifications"""
        count = UserNotification.objects.filter(
            user=request.user, 
            is_read=False
        ).count()
        
        return Response({'unread_count': count})
