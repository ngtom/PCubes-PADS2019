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
    # table = build_table(log, request.GET.get('page', 1))

    if(request.POST.get('add_dim')):
        new_dim = Dimension.objects.create(log=log, name='Dimension ')
        # new_dim.save()

    elif(request.POST.get('del_dim')):
        dim_id = request.POST.get('dim_id')
        dimension = Dimension.objects.get(pk=dim_id)
        dimension.delete()

    elif(request.POST.get('rem_attr')):
        dim_id = request.POST.get('dim_id')
        attr_id = request.POST.get('attr_id')

        dimension = Dimension.objects.get(pk=dim_id)
        for attr in dimension.attributes:
            if(attr.pk == attr_id):
                dimension.attributes.remove(attr)

        dimension.save()

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

    json = dumps(attributes)
    # return HttpResponse(attributes, content_type='application/json')
    return JsonResponse(attributes, safe=False)


def build_table(log, page):
    # TODO: maybe not the best way to connect to the db
    client = MongoClient(host=DATABASES['default']['HOST'])
    db = client[DATABASES['default']['NAME']]
    event_collection = db['events']

    t1 = time.time()
    events = event_collection.find({'log': log.id})
    # events = [rem_id(e) for e in events]

    attributes = Attribute.objects.filter(log=log)

    def column(attribute):
        if(attribute.parent == 'trace'):
            name = attribute.parent + ':' + attribute.name
        else:
            name = attribute.name
        return (name, tables.Column(verbose_name=name))

    attr_names = [column(a) for a in attributes]

    page_size = 10
    # events = events.skip(page_size * (page - 1)).limit(page_size)

    t1 = time.time()
    log_table = Table(data=events, extra_columns=attr_names)
    t2 = time.time()
    print("build table: " + str(t2 - t1))
    log_table.paginate(page=page, per_page=10)

    return log_table
