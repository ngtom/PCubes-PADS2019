from django.shortcuts import render
from import_xes.models import Attribute, Dimension, ProcessCube, EventLog
from itertools import product, chain
from bson.json_util import dumps
from django.http import JsonResponse
import json

# Create your views here.


def get_dim_values(dimension):
    attributes = dimension.attributes.all()
    values_lists = [a.values for a in attributes]

    values = list(product(*values_lists))
    values = [list(v) for v in values]

    return values


def list_cells(request, log_id, cube_id):
    logs = EventLog.objects.all()
    log = EventLog.objects.get(pk=log_id)
    cubes = ProcessCube.objects.filter(log=log)
    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)

    return render(request, "cells_list/cells_list.html", {
        'log': log,
        'cube': cube,
        'logs': logs,
        'cubes': cubes,
        'dimensions': dimensions,
    })


def get_cells(request, log_id, cube_id):
    log = EventLog.objects.get(pk=log_id)
    cubes = ProcessCube.objects.filter(log=log)
    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)

    dim_values_list = [get_dim_values(dim) for dim in dimensions]

    value_combinations = list(product(*dim_values_list))
    value_combinations = [list(chain.from_iterable(vs))
                               for vs in value_combinations]

    return JsonResponse(value_combinations, safe=False)


def model(request, log_id, cube_id):
    values = request.POST.get("values")
    values = json.loads(values)
    
    values_ = {}

    for k in values:
        if(k.startswith('event:')):
            values_[k[6:]] = values[k]
        else:
            values_[k] = values[k]

    values = values_
    print(values)
    return JsonResponse(values, safe=False)
