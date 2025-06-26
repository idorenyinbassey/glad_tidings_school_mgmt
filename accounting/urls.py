from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    path('', views.accounting_home, name='accounting_home'),
    path('fees/', views.fees, name='fees'),
    path('reports/', views.reports, name='reports'),
]
