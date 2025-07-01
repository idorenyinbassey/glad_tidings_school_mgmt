from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    # Main pages
    path('', views.accounting_home, name='home'),
    path('fees/', views.fees, name='fees'),
    path('reports/', views.reports, name='reports'),
    
    # Tuition Fee Management
    path('fees/list/', views.fee_list, name='fee_list'),
    path('fees/create/', views.fee_create, name='fee_create'),
    path('fees/<int:pk>/', views.fee_detail, name='fee_detail'),
    path('fees/<int:pk>/edit/', views.fee_edit, name='fee_edit'),
    
    # Payment Management
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/create/<int:fee_pk>/', views.payment_create, name='payment_create_for_fee'),
    
    # Expense Management
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    
    # Payroll Management
    path('payroll/', views.payroll_list, name='payroll_list'),
    
    # AJAX endpoints
    path('ajax/student-search/', views.student_search_ajax, name='student_search_ajax'),
    path('ajax/fee-statistics/', views.fee_statistics_ajax, name='fee_statistics_ajax'),
    path('ajax/generate-report/', views.generate_report_ajax, name='generate_report_ajax'),
    path('ajax/dashboard-stats/', views.dashboard_stats_ajax, name='dashboard_stats_ajax'),
    
    # Payroll Management
    path('payroll/generate/', views.generate_payroll_ajax, name='generate_payroll_ajax'),
]
