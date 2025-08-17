from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    # Result Management URLs
    path('', views.result_dashboard, name='result_dashboard'),
    path('entry/', views.result_entry, name='result_entry'),
    path('compile/', views.compile_results, name='compile_results'),
    path('sheets/', views.result_sheets, name='result_sheets'),
    path('print/<int:sheet_id>/', views.print_result_sheet, name='print_result_sheet'),
    path('bulk-upload/', views.bulk_upload_results, name='bulk_upload_results'),
    path('csv-template/', views.download_csv_template, name='download_csv_template'),
    
    # AJAX endpoints
    path('api/class-students/', views.get_class_students, name='get_class_students'),
    path('api/class-averages/', views.class_averages_api, name='class_averages_api'),
]
