from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_home, name='staff_home'),
    path('timetable/', views.timetable, name='timetable'),
    path('assignments/', views.assignments, name='assignments'),
    path('performance/', views.performance, name='performance'),
    path('attendance/', views.attendance, name='attendance'),
]
