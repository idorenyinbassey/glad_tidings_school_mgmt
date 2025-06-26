from django.urls import path
from . import password_views

app_name = 'users'

urlpatterns = [
    # Password reset URLs
    path('password-reset/', 
         password_views.CustomPasswordResetView.as_view(), 
         name='password_reset'),
    path('password-reset/done/', 
         password_views.CustomPasswordResetDoneView.as_view(), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         password_views.CustomPasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('reset/done/', 
         password_views.CustomPasswordResetCompleteView.as_view(), 
         name='password_reset_complete'),
    
    # Password change URLs
    path('password-change/', 
         password_views.CustomPasswordChangeView.as_view(), 
         name='password_change'),
    path('password-change/done/', 
         password_views.CustomPasswordChangeDoneView.as_view(), 
         name='password_change_done'),
]
