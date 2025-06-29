"""
URL configuration for glad_school_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Simple health check for Docker
@csrf_exempt
def health_check(request):
    """Health check endpoint for Docker and load balancers"""
    return JsonResponse({'status': 'healthy', 'service': 'glad_school_portal'})

# Custom error handlers
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'
handler403 = 'core.views.custom_403'

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    # Include our custom user password URLs before the default auth URLs
    path('accounts/', include('users.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('students/', include('students.urls')),
    path('staff/', include('staff.urls')),
    path('academics/', include('academics.urls')),
    path('assignments/', include('assignments.urls')),
    path('accounting/', include('accounting.urls')),
    path('itsupport/', include('itsupport.urls')),
    path('cbt/', include('cbt.urls')),
    
    # Django REST Framework browsable API (development only)
    path('api-auth/', include('rest_framework.urls')) if settings.DEBUG else path('', lambda r: None),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Add debug toolbar URLs
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
