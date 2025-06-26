from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('', views.academics_home, name='academics_home'),
    path('elibrary/', views.elibrary, name='elibrary'),
    path('timetable/', views.timetable, name='timetable'),
]
