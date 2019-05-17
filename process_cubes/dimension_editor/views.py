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

    def column(attribute):
        if(attribute.parent == 'trace'):
            name = attribute.parent + ':' + attribute.name
        else:
            name = attribute.name
        return name

    attr_names = [column(a) for a in attributes]

    return render(request, 'dimension_editor/main.html',
                  {
                      'log': log,
                      'dimensions': dimensions,
                      'attributes': attr_names
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


def remove_dimension(request, pk):
    dim_id = request.POST.get('dim_id')
    dimension = Dimension.objects.get(pk=dim_id)
    dimension.delete()

    return JsonResponse(dim_id, safe=False)

def add_dimension(request, pk):
    log = EventLog.objects.get(pk=pk)
    new_dim = Dimension.objects.create(log=log, name='Dimension ')
    
    data = {'dim_id': new_dim.id, 'dim_name': new_dim.name}

    return JsonResponse(data)
