from rest_framework import serializers
from .models import UserNotification


class UserNotificationSerializer(serializers.ModelSerializer):
    """Serializer for UserNotification model"""
    
    class Meta:
        model = UserNotification
        fields = ['id', 'title', 'message', 'link', 'created_at', 'is_read']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        # Set the user from the request context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)
