from django.shortcuts import render

from import_xes.models import EventLog

# Create your views here.

def dimension_edit(request, pk):
    log = EventLog.objects.get(pk=pk)
    