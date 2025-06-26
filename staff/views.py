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
    # In a real application, you would fetch assignments for the staff to grade
    context = {
        'assignments': []
    }
    return render(request, 'staff/assignments.html', context)

@login_required
def performance(request):
    # In a real application, you would fetch student performance data for the staff
    context = {
        'performance_data': []
    }
    return render(request, 'staff/performance.html', context)

@login_required
def attendance(request):
    # In a real application, you would fetch attendance data for the staff to manage
    context = {
        'attendance_data': []
    }
    return render(request, 'staff/attendance.html', context)
