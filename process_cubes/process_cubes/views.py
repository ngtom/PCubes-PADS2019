from django.shortcuts import render, redirect
# Create your views here.

from django.http import HttpResponse
from import_xes.models import EventLog, import_xes, ProcessCube
from dimension_editor.views import dimension_edit


def home(request):
    eventlogs = EventLog.objects.all()
    return render(request, 'home.html', {'logs': eventlogs})


def log(request, log_id):
    eventlog = EventLog.objects.get(pk=log_id)
    cubes = ProcessCube.objects.filter(log=eventlog)
    logs = EventLog.objects.all()

    return render(request, 'log.html', {'log': eventlog, 'cubes': cubes, 'logs': logs})


def create_cube(request, log_id):
    eventlog = EventLog.objects.get(pk=log_id)
    name = request.POST.get('cube_name')

    print(name)
    cube = ProcessCube.objects.create(name=name, log=eventlog)
    
    return redirect(dimension_edit, log_id, cube.pk)
