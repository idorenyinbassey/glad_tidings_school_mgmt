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
    path('attendance/admin/students/manage/', views_attendance.manage_student_attendance, name='manage_student_attendance'),
    path('attendance/admin/staff/manage/', views_attendance.manage_staff_attendance, name='manage_staff_attendance'),
    path('profile/', views_profile.profile, name='profile'),
    # Admin profile management
    path('admin/students/', views_profile.admin_students_list, name='admin_students_list'),
    path('admin/students/<int:student_id>/', views_profile.admin_student_detail, name='admin_student_detail'),
    path('admin/staff/', views_profile.admin_staff_list, name='admin_staff_list'),
    path('admin/staff/<int:staff_id>/', views_profile.admin_staff_detail, name='admin_staff_detail'),
    # Public listings
    path('news/', views.news_list, name='news_list'),
    path('events/', views.events_list, name='events_list'),

    # Include API URLs
    path('', include('core.api_urls')),
]
