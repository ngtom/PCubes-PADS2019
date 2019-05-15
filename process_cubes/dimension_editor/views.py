from django.shortcuts import render

from import_xes.models import EventLog, Dimension, Attribute
from django_tables2 import Table
import django_tables2 as tables
from .tables import LogTable
from pymongo import MongoClient
from process_cubes.settings import DATABASES
# Create your views here.


def dimension_edit(request, pk):
    log = EventLog.objects.get(pk=pk)
    dimensions = Dimension.objects.filter(log=log)
    table = build_table(log)

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


def build_table(log):
    # TODO: maybe not the best way to connect to the db
    client = MongoClient(host=DATABASES['default']['HOST'])
    db = client[DATABASES['default']['NAME']]
    trace_collection = db['traces']
    event_collection = db['events']

    traces = trace_collection.find({'log': log.pk})

    def rem_id(event):
        event.pop('_id', '')
        return event

    table = []
    for trace in traces:
        events = event_collection.find({'trace:_id': trace['_id']})
        events = [rem_id(e) for e in events]
        table.append(events)

    attributes = Attribute.objects.filter(log=log)

    def column(attribute):
        name = attribute.parent + ':' + attribute.name
        return (name, tables.Column(verbose_name=name))

    attr_names = [column(a) for a in attributes]

    print(table)
    log_table = LogTable(data=table, extra_columns=attr_names)
    log_table.paginate(page=1, per_page=50)

    return log_table
