from django.urls import path
from . import views

app_name = 'cbt'

urlpatterns = [
    path('', views.cbt_home, name='cbt_home'),
    path('exams/', views.exams, name='exams'),
    path('results/', views.results, name='results'),
]
