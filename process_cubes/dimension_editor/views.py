from django.shortcuts import render

from import_xes.models import EventLog, Dimension, Attribute, ProcessCube
from slice_dice.models import Slice, Dice
from django_tables2 import Table
import django_tables2 as tables
import time
from django.core.paginator import Paginator
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from bson.json_util import dumps
from operator import mul
from functools import reduce
from django.template.loader import render_to_string
from .models import NumericalHierarchy, DateHierarchy
from datetime import timedelta
# Create your views here.


def dimension_edit(request, log_id, cube_id):
    log = EventLog.objects.get(pk=log_id)
    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)

    attributes = Attribute.objects.filter(log=log)

    used_attributes = [
        attr for dim in dimensions for attr in dim.attributes.all()]
    free_attributes = [
        attr for attr in attributes if attr not in used_attributes]

    cells = cube.get_num_cells()

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
                      'cells': cells,
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
        num_elements = dimension.get_num_elements()

    cube = ProcessCube.objects.get(pk=cube_id)

    cells = cube.get_num_cells()

    d_slice = Slice.objects.filter(dimension=dimension)
    d_dice = Dice.objects.filter(dimension=dimension)
    d_slice.delete()
    d_dice.delete()

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

    cells = cube.get_num_cells()

    if(len(dim.attributes.all()) == 0):
        num_elements = 0
    else:
        num_elements = dim.get_num_elements()

    data = {'attribute': attribute}
    html = render_to_string(
        'dimension_editor/dropdown_button.html', data, request)
    ret = {"html": html, 'num_elements': num_elements, 'cells': cells}

    d_slice = Slice.objects.filter(dimension=dim)
    d_dice = Dice.objects.filter(dimension=dim)
    d_slice.delete()
    d_dice.delete()

    return JsonResponse(ret)


def remove_dimension(request, log_id, cube_id):
    dim_id = request.POST.get('dim_id')
    dimension = Dimension.objects.get(pk=dim_id)
    dimension.delete()

    cube = ProcessCube.objects.get(pk=cube_id)
    cells = cube.get_num_cells()

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


def save_step(request, log_id, cube_id):
    if(request.method == "POST"):
        dim_id = request.POST.get('dim_id')
        attr_id = request.POST.get('attr_id')
        dtype = request.POST.get('dtype')

        dimension = Dimension.objects.get(pk=dim_id)
        attribute = Attribute.objects.get(pk=attr_id)

        if(dtype == 'float'):
            step = float(request.POST.get('step'))
            try:
                hier = NumericalHierarchy.objects.get(
                    attribute=attribute, dimension=dimension)
                hier.step_size = step
                hier.save()
            except NumericalHierarchy.DoesNotExist:
                hier = NumericalHierarchy(
                    dimension=dimension, attribute=attribute, step_size=step)
                hier.save()
        elif(dtype == 'date'):
            step = int(request.POST.get('step'))
            try:
                hier = DateHierarchy.objects.get(
                    attribute=attribute, dimension=dimension)
                hier.step_size = step
                hier.save()
            except DateHierarchy.DoesNotExist:
                hier = DateHierarchy(dimension=dimension,
                                     attribute=attribute, step_size=step)
                hier.save()

        num_elements = dimension.get_num_elements()
        cube = ProcessCube.objects.get(pk=cube_id)
        cells = cube.get_num_cells()

        ret = {'num_elements': num_elements, 'cells': cells}

        d_slice = Slice.objects.filter(dimension=dimension)
        d_dice = Dice.objects.filter(dimension=dimension)
        d_slice.delete()
        d_dice.delete()

        return JsonResponse(ret)

    return HttpResponse()
