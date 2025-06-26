from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def academics_home(request):
    return render(request, 'academics/academics_home.html')

@login_required
def elibrary(request):
    # In a real application, you would fetch e-library resources
    context = {
        'resources': []
    }
    return render(request, 'academics/elibrary.html', context)

@login_required
def timetable(request):
    # In a real application, you would fetch class timetables
    context = {
        'timetables': []
    }
    return render(request, 'academics/timetable.html', context)
