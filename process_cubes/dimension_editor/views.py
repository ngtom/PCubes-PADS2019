from django.shortcuts import render

from import_xes.models import EventLog, Dimension

# Create your views here.

def dimension_edit(request, pk):
    log = EventLog.objects.get(pk=pk)
    
    dimensions = Dimension.objects.get(log=log)
