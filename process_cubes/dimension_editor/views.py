from django.shortcuts import render

from import_xes.models import EventLog, Dimension, Attribute
from django_tables2 import Table
import django_tables2 as tables
# from .tables import LogTable
from pymongo import MongoClient
from process_cubes.settings import DATABASES
import time

# Create your views here.


def dimension_edit(request, pk):
    log = EventLog.objects.get(pk=pk)
    dimensions = Dimension.objects.filter(log=log)
    table = build_table(log, request.GET.get('page', 1))

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

    return render(request, 'dimension_editor/main.html',
                  {
                      'log': log,
                      'dimensions': dimensions,
                      'table': table
                  })


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

    t1 = time.time()
    log_table = Table(data=events, extra_columns=attr_names)
    t2 = time.time()
    print("build table: " + str(t2 - t1))
    log_table.paginate(page=page, per_page=10)

    return log_table
