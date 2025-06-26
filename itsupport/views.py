from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def itsupport_home(request):
    return render(request, 'itsupport/itsupport_home.html')

@login_required
def system_health(request):
    # In a real application, you would fetch system health data
    context = {
        'system_health': []
    }
    return render(request, 'itsupport/system_health.html', context)

@login_required
def troubleshooting(request):
    # In a real application, you would fetch troubleshooting logs
    context = {
        'logs': []
    }
    return render(request, 'itsupport/troubleshooting.html', context)

@login_required
def access_requests(request):
    # In a real application, you would fetch user access requests
    context = {
        'requests': []
    }
    return render(request, 'itsupport/access_requests.html', context)

@login_required
def bug_reports(request):
    # In a real application, you would fetch bug reports
    context = {
        'bugs': []
    }
    return render(request, 'itsupport/bug_reports.html', context)
