from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required
def student_home(request):
    return render(request, 'students/student_home.html')

@login_required
def assignments(request):
    # In a real application, you would fetch assignments for the student
    context = {
        'assignments': []
    }
    return render(request, 'students/assignments.html', context)

@login_required
def results(request):
    # In a real application, you would fetch results for the student
    context = {
        'results': []
    }
    return render(request, 'students/results.html', context)

@login_required
def attendance(request):
    # In a real application, you would fetch attendance for the student
    context = {
        'attendance': []
    }
    return render(request, 'students/attendance.html', context)
