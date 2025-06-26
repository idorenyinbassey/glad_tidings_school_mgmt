from django.urls import path
from . import views

app_name = 'itsupport'

urlpatterns = [
    path('', views.itsupport_home, name='itsupport_home'),
    path('systemhealth/', views.system_health, name='system_health'),
    path('troubleshooting/', views.troubleshooting, name='troubleshooting'),
    path('access/', views.access_requests, name='access_requests'),
    path('bugs/', views.bug_reports, name='bug_reports'),
]
