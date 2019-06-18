from django.shortcuts import render
from import_xes.models import Attribute, Dimension, ProcessCube, EventLog
from itertools import product, chain
from slice_dice.models import Slice, Dice
from dimension_editor.models import DateHierarchy, NumericalHierarchy
from bson.json_util import dumps
from django.http import JsonResponse
import json
from datetime import datetime
import math

# Create your views here.


def get_dim_values(dimension):
    attributes = dimension.attributes.all()
    values_lists = []
    skips = []
    for attribute in attributes:
        step = 1
        if(attribute.dtype == "int" or attribute.dtype == "float"):
            try:
                hierarchy = NumericalHierarchy.objects.get(
                    attribute=attribute, dimension=dimension)
                step = hierarchy.step_size
                skips.append(hierarchy.step_size)
            except NumericalHierarchy.DoesNotExist:
                skips.append(1)
        elif(attribute.dtype == "date"):
            try:
                hierarchy = DateHierarchy.objects.get(
                    attribute=attribute, dimension=dimension)
                step = hierarchy.step_size
                skips.append(hierarchy.step_size)
            except DateHierarchy.DoesNotExist:
                skips.append(1)

        orig_values = sorted(attribute.values)
        range_values = []

        num_values = math.ceil(len(orig_values) / step)
        for i in range(num_values):
            lower = orig_values[i * step]
            if(step > 1):
                upper_ind = (i + 1) * step
                if(upper_ind >= len(orig_values)):
                    upper_ind = len(orig_values) - 1

                upper = orig_values[upper_ind]
                range_values.append('{} to {}'.format(lower, upper))
            else:
                range_values.append(lower)

        values_lists.append(range_values)

    values = list(product(*values_lists))
    values = [list(v) for v in values]

    return values


def get_restricted_dim_values(dimension):
    attributes = dimension.attributes.all()

    d_slice = Slice.objects.filter(dimension=dimension)
    d_dice = Dice.objects.filter(dimension=dimension)

    if(d_slice.exists()):
        restrictions = d_slice[0].value.values
        values = {r.attribute.pk: r.value for r in restrictions}
        values_lists = [[values[a.pk]] for a in attributes]
    elif(d_dice.exists()):
        restrictions = d_dice[0].values
        values = {a.pk: [] for a in attributes}
        for dr in restrictions:
            for ar in dr.values:
                values[ar.attribute.pk].append(ar.value)

        values_lists = [values[a.pk] for a in attributes]
    else:
        values_lists = []
        for attribute in attributes:
            step = 1
            if(attribute.dtype == "int" or attribute.dtype == "float"):
                try:
                    hierarchy = NumericalHierarchy.objects.get(
                        attribute=attribute, dimension=dimension)
                    step = hierarchy.step_size
                except NumericalHierarchy.DoesNotExist:
                    step = 1
            elif(attribute.dtype == "date"):
                try:
                    hierarchy = DateHierarchy.objects.get(
                        attribute=attribute, dimension=dimension)
                    step = hierarchy.step_size
                except DateHierarchy.DoesNotExist:
                    step = 1

            orig_values = sorted(attribute.values)
            range_values = []

            num_values = math.ceil(len(orig_values) / step)
            for i in range(num_values):
                lower = orig_values[i * step]
                if(step > 1):
                    upper_ind = (i + 1) * step
                    if(upper_ind >= len(orig_values)):
                        upper_ind = len(orig_values) - 1

                    upper = orig_values[upper_ind]
                    range_values.append('{} to {}'.format(lower, upper))
                else:
                    range_values.append(lower)

            values_lists.append(range_values)

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

    dim_values_list = [get_restricted_dim_values(dim) for dim in dimensions]

    value_combinations = list(product(*dim_values_list))
    value_combinations = [list(chain.from_iterable(vs))
                          for vs in value_combinations]

    return JsonResponse(value_combinations, safe=False)


def model(request, log_id, cube_id):
    values = request.POST.get("values")
    if(values == None):
        values = "{}"
    values = json.loads(values)
    
    def convert(value, dtype):
        if(dtype == 'float'):
            return float(value)
        elif(dtype == 'int'):
            return int(value)
        elif(dtype == 'date'):
            return convert_date(value)
        elif(dtype == 'bool'):
            return bool(value)
        else:
            return value

    def convert_date(value):
        # Construct datetime object to filter with pymongo
        time_format = "%Y-%m-%dT%H:%M:%S.%f"
        time_format = "%Y-%m-%d %H:%M:%S.%f"
        if("." not in value):
            time_format = time_format[:-3]

        return datetime.strptime(value, time_format)

    values_ = {}

    # Convert to attribute id to name like it is in the events.
    values_ = {}
    for key in values:
        if(key != 'log'):
            attribute = Attribute.objects.get(pk=key)
            if(":" in attribute.parent):
                parent = attribute.parent.split(':')[0]
                d_name = attribute.parent.split(':')[1]
                name = attribute.name

                # Query for elements of dictionary
                queryname = parent + ":" + d_name + ".children." + name
            else:
                queryname = attribute.name
                if(attribute.parent == "trace"):
                    queryname = 'trace:' + queryname

            if("to" in values[key]):
                lower = values[key].split("to")[0].strip()
                upper = values[key].split('to')[1].strip()

                lower = convert(lower, attribute.dtype)
                upper = convert(upper, attribute.dtype)

                values_[queryname] = {'$gt': lower, '$lt': upper}
            else:
                value = convert(values[key], attribute.dtype)
                values_[queryname] = value

    values_['log'] = log_id
    values = values_

    return JsonResponse(values, safe=False)
