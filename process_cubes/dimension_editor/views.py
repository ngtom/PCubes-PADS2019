from django.shortcuts import render

from import_xes.models import EventLog, Dimension, Attribute, ProcessCube
from django_tables2 import Table
import django_tables2 as tables
from pymongo import MongoClient
from process_cubes.settings import DATABASES
import time
from django.core.paginator import Paginator
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from bson.json_util import dumps

# Create your views here.


def dimension_edit(request, log_id, cube_id):
    log = EventLog.objects.get(pk=log_id)
    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)

    # used_attributes = Attribute.objects.filter(log=log).exclude(dimension__in=dimensions)
    # print(used_attributes)

    attributes = Attribute.objects.filter(log=log)
    used_attributes = [attr for dim in dimensions for attr in dim.attributes.all()]
    free_attributes = [attr for attr in attributes if attr not in used_attributes]


    return render(request, 'dimension_editor/main.html',
                  {
                      'log': log,
                      'dimensions': dimensions,
                      'attributes': attributes,
                      'free_attributes': free_attributes,
                  })


def get_dimensions(request, log_id, cube_id):
    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)

    json = dumps(dimensions)
    # return HttpResponse(attributes, content_type='application/json')
    return JsonResponse(json, safe=False)


def add_attribute(request, log_id, cube_id):
    dim_id = request.POST.get('dim_id')
    attr_id = request.POST.get('attr_id')

    dimension = Dimension.objects.get(pk=dim_id)
    attribute = Attribute.objects.get(pk=attr_id)

    dimension.attributes.add(attribute)
    dimension.save()

    data = {'dim': dimension, 'attribute': attribute}
    return render(request, 'dimension_editor/attribute.html', data)


def rem_attribute(request, log_id, cube_id):
    dim_id = request.POST.get('dim_id')
    attr_id = request.POST.get('attr_id')

    dim = Dimension.objects.get(pk=dim_id)

    attribute = Attribute.objects.get(pk=attr_id)
    dim.attributes.remove(attribute)
    dim.save()

    data = {'attribute': attribute}
    return render(request, 'dimension_editor/dropdown_button.html', data)


def remove_dimension(request, log_id, cube_id):
    dim_id = request.POST.get('dim_id')
    dimension = Dimension.objects.get(pk=dim_id)
    dimension.delete()

    return JsonResponse(dim_id, safe=False)


def add_dimension(request, log_id, cube_id):
    log = EventLog.objects.get(pk=log_id)
    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)
    
    new_dim = Dimension.objects.create(cube=cube, name='Dimension')

    attributes = Attribute.objects.filter(log=log)
    used_attributes = [attr for dim in dimensions for attr in dim.attributes.all()]
    free_attributes = [attr for attr in attributes if attr not in used_attributes]

    data = {'dim': new_dim, 'free_attributes': free_attributes}
    return render(request, 'dimension_editor/dimension.html', data)
