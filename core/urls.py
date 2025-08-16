from django.urls import path, include
from . import views, views_notifications, views_performance, views_elibrary, views_attendance, views_profile

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('about-us/', views.about_us, name='about_us'),
    path('admission/', views.admission, name='admission'),
    path('contact/', views.contact_us, name='contact_us'),
    path('academics/', views.academics_page, name='academics'),
    path('portal/', views.portal, name='portal'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notifications/', views_notifications.notifications, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', views_notifications.mark_notification_read, name='mark_notification_read'),
    path('notifications/unread-count/', views_notifications.get_unread_count, name='notification_unread_count'),
    path('performance/', views_performance.performance_analytics, name='performance_analytics'),
    path('elibrary/', views_elibrary.elibrary, name='elibrary'),
    path('attendance/', views_attendance.attendance, name='attendance'),
    path('profile/', views_profile.profile, name='profile'),
    # Public listings
    path('news/', views.news_list, name='news_list'),
    path('events/', views.events_list, name='events_list'),

    # Include API URLs
    path('', include('core.api_urls')),
]
