from django.shortcuts import render

from import_xes.models import EventLog, Dimension, Attribute
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


def dimension_edit(request, pk):
    log = EventLog.objects.get(pk=pk)
    dimensions = Dimension.objects.filter(log=log)
    attributes = Attribute.objects.filter(log=log)
    free_attributes = Attribute.objects.filter(log=log, dimension=None)
    def column(attribute):
        if(attribute.parent == 'trace'):
            name = attribute.parent + ':' + attribute.name
        else:
            name = attribute.name
        return name

    # attr_names = [column(a) for a in attributes]

    return render(request, 'dimension_editor/main.html',
                  {
                      'log': log,
                      'dimensions': dimensions,
                      'attributes': attributes,
                      'free_attributes': free_attributes,
                  })


def get_events(request, pk):
    client = MongoClient(host=DATABASES['default']['HOST'])
    db = client[DATABASES['default']['NAME']]
    event_collection = db['events']

    def rem_id(e):
        e.pop("_id", "")
        return e

    events = event_collection.find({'log': pk})
    events = [rem_id(e) for e in events]

    log = EventLog.objects.get(pk=pk)
    attributes = Attribute.objects.filter(log=log)

    events_json = dumps({'data': events})

    return HttpResponse(events_json, content_type='application/json')


def get_attrs(request, pk):
    log = EventLog.objects.get(pk=pk)
    attributes = Attribute.objects.filter(log=log)

    def attr(attribute):
        if(attribute.parent == 'trace'):
            name = attribute.parent + ':' + attribute.name
        else:
            name = attribute.name
        return name

    attributes = [{'data': attr(a)} for a in attributes]

    # return HttpResponse(attributes, content_type='application/json')
    return JsonResponse(attributes, safe=False)


def get_dimensions(request, pk):
    log = EventLog.objects.get(pk=pk)
    dimensions = Dimension.objects.filter(log=log)

    json = dumps(dimensions)
    # return HttpResponse(attributes, content_type='application/json')
    return JsonResponse(json, safe=False)


def get_free_attributes(request, pk):
    log = EventLog.objects.get(pk=pk)
    dimensions = Dimension.objects.filter(log=log)

    for dimension in dimensions:
        print(dimension.attributes)

    # used_attributes = [attr for dimension in dimensions for attr in Dimension.attributes]
    # print(used_attributes)

    return JsonResponse("used_attributes", safe=False)


def add_attribute(request, pk):
    dim_id = request.POST.get('dim_id')
    attr_id = request.POST.get('attr_id')

    dimension = Dimension.objects.get(pk=dim_id)
    attribute = Attribute.objects.get(pk=attr_id)

    attribute.dimension = dimension
    attribute.save()

    data = {'dim': dimension, 'attribute': attribute}
    return render(request, 'dimension_editor/attribute.html', data)


def rem_attribute(request, pk):
    dim_id = request.POST.get('dim_id')
    attr_id = request.POST.get('attr_id')

    dim = Dimension.objects.get(pk=dim_id)

    attribute = Attribute.objects.get(pk=attr_id)
    attribute.dimension = None
    attribute.save()

    data = {'attribute': attribute}
    return render(request, 'dimension_editor/dropdown_button.html', data)


def remove_dimension(request, pk):
    dim_id = request.POST.get('dim_id')
    dimension = Dimension.objects.get(pk=dim_id)
    dimension.delete()

    return JsonResponse(dim_id, safe=False)


def add_dimension(request, pk):
    log = EventLog.objects.get(pk=pk)
    new_dim = Dimension.objects.create(log=log, name='Dimension')

    attributes = Attribute.objects.filter(log=log)
    free_attributes = Attribute.objects.filter(log=log, dimension=None)

    data = {'dim': new_dim, 'attributes': attributes, 'free_attributes': free_attributes}
    return render(request, 'dimension_editor/dimension.html', data)
