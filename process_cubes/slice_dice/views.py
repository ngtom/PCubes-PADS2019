from django.shortcuts import render
from import_xes.models import EventLog, Dimension, Attribute, ProcessCube

# Create your views here.


def slice(request, log_id, cube_id, dim_id):
    logs = EventLog.objects.all()
    log = EventLog.objects.get(pk=log_id)
    cubes = ProcessCube.objects.filter(log=log)
    cube = ProcessCube.objects.get(pk=cube_id)
    dimension = Dimension.objects.filter(pk=dim_id)

    return render(request, "cells_list/cells_list.html", {
        'log': log,
        'cube': cube,
        'logs': logs,
        'cubes': cubes,
        'dim': dimension,
    })

    

def dice_operation(request, pk):
    log = EventLog.objects.get(pk=pk)
    