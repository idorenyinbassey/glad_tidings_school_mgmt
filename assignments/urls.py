from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('', views.assignments_home, name='assignments_home'),
    path('student/', views.student_assignments, name='student_assignments'),
    path('staff/', views.staff_assignments, name='staff_assignments'),
    path('submit/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('grade/<int:submission_id>/', views.grade_submission, name='grade_submission'),
]
