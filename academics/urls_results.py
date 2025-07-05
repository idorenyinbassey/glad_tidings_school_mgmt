from django.urls import path
from . import views_results

app_name = 'academics'

urlpatterns = [
    # Result Management URLs
    path('results/', views_results.result_dashboard, name='result_dashboard'),
    path('results/entry/', views_results.result_entry, name='result_entry'),
    path('results/compile/', views_results.compile_results, name='compile_results'),
    path('results/sheets/', views_results.result_sheets, name='result_sheets'),
    path('results/print/<int:sheet_id>/', views_results.print_result_sheet, name='print_result_sheet'),
    path('results/bulk-upload/', views_results.bulk_upload_results, name='bulk_upload_results'),
    path('results/csv-template/', views_results.download_csv_template, name='download_csv_template'),
    
    # AJAX endpoints
    path('api/class-students/', views_results.get_class_students, name='get_class_students'),
]
