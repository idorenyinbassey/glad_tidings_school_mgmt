from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

 
@login_required
def staff_home(request):
    return render(request, 'staff/staff_home.html')

 
@login_required
def timetable(request):
    # In a real application, you would fetch timetable for the staff
    context = {
        'timetable': []
    }
    return render(request, 'staff/timetable.html', context)

 
@login_required
def assignments(request):
    return HttpResponseRedirect(reverse('assignments:staff_assignments'))

 
@login_required
def performance(request):
    # In a real application, you would fetch student performance data for the staff
    context = {
        'performance_data': []
    }
    return render(request, 'staff/performance.html', context)

 
@login_required
def attendance(request):
    # Canonical attendance is handled in core.
    user = request.user
    if not hasattr(user, 'staff_profile'):
        return HttpResponseRedirect(reverse('attendance'))

    # Keep the staff page for any staff-specific extras if needed; otherwise, link to core.
    return HttpResponseRedirect(reverse('attendance'))
