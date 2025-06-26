from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def accounting_home(request):
    return render(request, 'accounting/accounting_home.html')

@login_required
def fees(request):
    # In a real application, you would fetch fee data
    context = {
        'fees': []
    }
    return render(request, 'accounting/fees.html', context)

@login_required
def reports(request):
    # In a real application, you would fetch financial reports
    context = {
        'reports': []
    }
    return render(request, 'accounting/reports.html', context)
