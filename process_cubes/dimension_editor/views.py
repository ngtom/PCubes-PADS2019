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
from operator import mul
from functools import reduce
from django.template.loader import render_to_string
# Create your views here.


def dimension_edit(request, log_id, cube_id):
    log = EventLog.objects.get(pk=log_id)
    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)

    # used_attributes = Attribute.objects.filter(log=log).exclude(dimension__in=dimensions)
    # print(used_attributes)

    attributes = Attribute.objects.filter(log=log)

    used_attributes = [
        attr for dim in dimensions for attr in dim.attributes.all()]
    free_attributes = [
        attr for attr in attributes if attr not in used_attributes]

    for dim in dimensions:
        if(len(dim.attributes.all()) > 0):
            dim.num_elements = reduce(
                mul, [len(attr.values) for attr in dim.attributes.all()], 1)

    cells = reduce(
        mul, [dim.num_elements for dim in dimensions if dim.num_elements != 0], 1)

    logs = EventLog.objects.all()
    cubes = ProcessCube.objects.filter(log=log)
    return render(request, 'dimension_editor/main.html',
                  {
                      'cube': cube,
                      'logs': logs,
                      'cubes': cubes,
                      'log': log,
                      'dimensions': dimensions,
                      'attributes': attributes,
                      'free_attributes': free_attributes,
                      'cells': cells
                  })


def get_dimensions(request, log_id, cube_id):
    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)

    json = dumps(dimensions)
    return JsonResponse(json, safe=False)


def add_attribute(request, log_id, cube_id):
    dim_id = request.POST.get('dim_id')
    attr_id = request.POST.get('attr_id')

    dimension = Dimension.objects.get(pk=dim_id)
    attribute = Attribute.objects.get(pk=attr_id)

    dimension.attributes.add(attribute)

    if(len(dimension.attributes.all()) == 0):
        num_elements = 0
    else:
        num_elements = reduce(mul, [len(attr.values)
                                    for attr in dimension.attributes.all()], 1)

    dimension.num_elements = num_elements
    dimension.save()

    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)
    for dim in dimensions:
        if(len(dim.attributes.all()) > 0):
            dim.num_elements = reduce(
                mul, [len(attr.values) for attr in dim.attributes.all()], 1)

    cells = reduce(
        mul, [dim.num_elements for dim in dimensions if dim.num_elements != 0], 1)

    data = {'dim': dimension, 'attribute': attribute}
    html = render_to_string('dimension_editor/attribute.html', data, request)
    ret = {"html": html, 'num_elements': num_elements, 'cells': cells}

    return JsonResponse(ret)


def rem_attribute(request, log_id, cube_id):
    dim_id = request.POST.get('dim_id')
    attr_id = request.POST.get('attr_id')

    dim = Dimension.objects.get(pk=dim_id)

    attribute = Attribute.objects.get(pk=attr_id)
    dim.attributes.remove(attribute)
    dim.save()

    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)
    for d in dimensions:
        if(len(d.attributes.all()) > 0):
            d.num_elements = reduce(
                mul, [len(attr.values) for attr in d.attributes.all()], 1)

    cells = reduce(
        mul, [dim.num_elements for dim in dimensions if dim.num_elements != 0], 1)

    if(len(dim.attributes.all()) == 0):
        num_elements = 0
    else:
        num_elements = reduce(mul, [len(attr.values)
                                    for attr in dim.attributes.all()], 1)

    print(dim.pk)

    data = {'attribute': attribute}
    html = render_to_string(
        'dimension_editor/dropdown_button.html', data, request)
    ret = {"html": html, 'num_elements': num_elements, 'cells': cells}

    return JsonResponse(ret)


def remove_dimension(request, log_id, cube_id):
    dim_id = request.POST.get('dim_id')
    dimension = Dimension.objects.get(pk=dim_id)
    dimension.delete()

    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)
    for d in dimensions:
        if(len(d.attributes.all()) > 0):
            d.num_elements = reduce(
                mul, [len(attr.values) for attr in d.attributes.all()], 1)

    cells = reduce(
        mul, [dim.num_elements for dim in dimensions if dim.num_elements != 0], 1)

    data = {"cells": cells}

    return JsonResponse(data)


def add_dimension(request, log_id, cube_id):
    log = EventLog.objects.get(pk=log_id)
    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)

    new_dim = Dimension.objects.create(cube=cube, name='Dimension')
    print(new_dim.pk)
    attributes = Attribute.objects.filter(log=log)
    used_attributes = [
        attr for dim in dimensions for attr in dim.attributes.all()]
    free_attributes = [
        attr for attr in attributes if attr not in used_attributes]

    data = {'dim': new_dim, 'free_attributes': free_attributes}
    return render(request, 'dimension_editor/dimension.html', data)


def save_dim_name(request, log_id, cube_id):
    dim_id = request.POST.get('dim_id')
    dim_name = request.POST.get('dim_name')

    dimension = Dimension.objects.get(pk=dim_id)
    dimension.name = dim_name
    dimension.save()

    return HttpResponse('')