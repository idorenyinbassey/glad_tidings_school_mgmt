from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_home, name='student_home'),
    path('assignments/', views.assignments, name='assignments'),
    path('results/', views.results, name='results'),
    path('attendance/', views.attendance, name='attendance'),
    path('result-sheets/', views.result_sheets, name='result_sheets'),
    path('print-result/<int:session_id>/<int:term_id>/', views.print_result_sheet, name='print_result_sheet'),
]
