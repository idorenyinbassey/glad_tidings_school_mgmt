from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import UserNotificationViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'notifications', UserNotificationViewSet, basename='notification')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
