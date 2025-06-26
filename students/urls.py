from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_home, name='student_home'),
    path('assignments/', views.assignments, name='assignments'),
    path('results/', views.results, name='results'),
    path('attendance/', views.attendance, name='attendance'),
]
