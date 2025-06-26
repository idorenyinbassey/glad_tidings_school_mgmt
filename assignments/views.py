from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def assignments_home(request):
    return render(request, 'assignments/assignments_home.html')

@login_required
def student_assignments(request):
    # In a real application, you would fetch assignments for students
    context = {
        'assignments': []
    }
    return render(request, 'assignments/student_assignments.html', context)

@login_required
def staff_assignments(request):
    # In a real application, you would fetch assignments for staff to manage
    context = {
        'assignments': []
    }
    return render(request, 'assignments/staff_assignments.html', context)
