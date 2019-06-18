from django.shortcuts import render
from import_xes.models import EventLog, Dimension, Attribute, ProcessCube
from itertools import product, chain
import json
from slice_dice.models import Slice
from django.http import HttpResponse

# Create your views here.


def slice(request, log_id, cube_id, dim_id):
    logs = EventLog.objects.all()
    log = EventLog.objects.get(pk=log_id)
    cubes = ProcessCube.objects.filter(log=log)
    cube = ProcessCube.objects.get(pk=cube_id)
    dimension = Dimension.objects.get(pk=dim_id)
    attributes = Attribute.objects.filter(log=log)

    print(dim_id)
    print(dimension.name) 
    print(dimension.attributes) 

    return render(request, "slice.html", {
        'log': log,
        'cube': cube,
        'logs': logs,
        'cubes': cubes,
        'dim': dimension
    })

    

def dice(request, log_id, cube_id, dim_id):
    logs = EventLog.objects.all()
    log = EventLog.objects.get(pk=log_id)
    cubes = ProcessCube.objects.filter(log=log)
    cube = ProcessCube.objects.get(pk=cube_id)
    dimension = Dimension.objects.get(pk=dim_id)

    print(dim_id)
    print(dimension.name)

    return render(request, "dice.html", {
        'log': log,
        'cube': cube,
        'logs': logs,
        'cubes': cubes,
        'dim': dimension
    })
    
def slice_save(request, log_id, cube_id, dim_id):
    logs = EventLog.objects.all()
    log = EventLog.objects.get(pk=log_id)
    cubes = ProcessCube.objects.filter(log=log)
    cube = ProcessCube.objects.get(pk=cube_id)
    dimension = Dimension.objects.get(pk=dim_id)

    json_data = json.loads(request.body)
    print(json_data['element'])
    print(json_data['attribute'])

    slice = Slice(element=json_data['element'], attribute=json_data['attribute'], dimension = dimension)
    slice.save()

    return HttpResponse("OK")