from django.shortcuts import render
# Create your views here.

from django.http import HttpResponse
from import_xes.models import EventLog, import_xes


def home(request):
    eventlogs = EventLog.objects.all()
    return render(request, 'home.html', {'logs': eventlogs})
