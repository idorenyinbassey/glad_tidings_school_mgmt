from django.shortcuts import render
# Note: trivial change to trigger Django auto-reloader after adding templates
from django.contrib.auth.decorators import login_required

 
@login_required
def cbt_home(request):
    return render(request, 'cbt/cbt_home.html')

 
@login_required
def exams(request):
    # In a real application, you would fetch exams data
    context = {
        'exams': []
    }
    return render(request, 'cbt/exams.html', context)

 
@login_required
def results(request):
    # In a real application, you would fetch exam results
    context = {
        'results': []
    }
    return render(request, 'cbt/results.html', context)
