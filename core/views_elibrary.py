from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from academics.models import ELibraryResource
from django.db.models import Q

@login_required
def elibrary(request):
    query = request.GET.get('q', '')
    resources = ELibraryResource.objects.all()
    if query:
        resources = resources.filter(Q(title__icontains=query) | Q(author__icontains=query) | Q(description__icontains=query))
    return render(request, 'core/elibrary.html', {'resources': resources, 'query': query})
