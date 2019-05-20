from djongo import models
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.filtering.log.variants import variants_filter
from pymongo import MongoClient
from process_cubes.settings import DATABASES
from bson.json_util import dumps
import os
import time
from operator import mul
from functools import reduce

class EventLog(models.Model):
    name = models.CharField(max_length=255)
    xes_file = models.FileField(upload_to='documents/')


class ProcessCube(models.Model):
    name = models.CharField(max_length=255)
    log = models.ForeignKey(to=EventLog, on_delete=models.CASCADE)


class Attribute(models.Model):
    name = models.CharField(max_length=255)
    parent = models.CharField(max_length=32)# to distinguish trace and event
    log = models.ForeignKey(to=EventLog, on_delete=models.CASCADE)
    values = models.ListField(null=True)


class Dimension(models.Model):
    name = models.CharField(max_length=255)
    # log = models.ForeignKey(to=EventLog, on_delete=models.CASCADE)
    cube = models.ForeignKey(to=ProcessCube, on_delete=models.CASCADE)
    attributes = models.ArrayReferenceField(to=Attribute)

    num_elements = 0

# Pymongo is used directly to import events, because with Django models it's very slow for large files
# and I found no way to realize Models with "dynamic fields"


def import_xes(xes_file, filename):
    t_start = time.time()

    # TODO: maybe not the best way to connect to the db
    client = MongoClient(host=DATABASES['default']['HOST'])
    db = client[DATABASES['default']['NAME']]
    trace_collection = db['traces']
    event_collection = db['events']

    t1 = time.time()
    #raw log from file 
    log = xes_importer.import_log(xes_file)
    t2 = time.time()
    print('xes_importer.import_log: ' + str(t2 - t1))
    # delete file after import?
    # os.remove(xes_file)

    #insert and save the raw log into our data model
    event_log = EventLog(name=filename, xes_file=xes_file)
    event_log.save()
    log_id = event_log.id

    def add_log_id(trace):
        trace['log'] = log_id
        return trace

    def add_trace_attrs(e, trace):
        for tattr in trace:
            if tattr != 'log':
                e['trace:' + tattr] = trace[tattr]

        e['log'] = log_id
        return e

    # Collect all attributes
    t1 = time.time()
    event_attributes = {attr for trace in log for event in trace for attr in event}
    trace_attributes = {attr for trace in log for attr in trace.attributes}

    all_attributes = [Attribute(name=attr, parent='event', log=event_log, values=[]) for attr in event_attributes] + [
        Attribute(name=attr, parent='trace', log=event_log, values=[]) for attr in trace_attributes]

    #This method inserts the provided list of objects into the database in an efficient manner
    Attribute.objects.bulk_create(all_attributes)

    print(all_attributes[0].id)

    t2 = time.time()
    print('time to find all attributes list: ' + str(t2 - t1))
    print(all_attributes)

    # Collect traces + events
    t1 = time.time()
    all_traces = [add_log_id(trace.attributes) for trace in log]
    trace_collection.insert_many(all_traces, ordered=False)
    t2 = time.time()
    print('collect and save traces: ' + str(t2 - t1))

    t1 = time.time()
    all_events = [add_trace_attrs(event._dict, trace.attributes)
                  for trace in log for event in trace._list]
    t2 = time.time()
    print('time to construct events list: ' + str(t2 - t1))

    print('#Traces: ' + str(len(all_traces)))
    print('#Events: ' + str(len(all_events)))

    t1 = time.time()

    def is_dict(v):
        if(type(v) is dict):
            return dumps(v)
        else:
            return v

    all_attributes = Attribute.objects.filter(log=event_log)

    for attribute in all_attributes:
        name = attribute.name
        if(attribute.parent == 'trace'):
            name = 'trace:' + name

        values = {is_dict(event[name])
                  for event in all_events if name in event}
        attribute.values = sorted(list(values))
        attribute.save()

    t2 = time.time()
    print('time to get values of attributes: ' + str(t2 - t1))

    t1 = time.time()
    event_collection.insert_many(all_events, ordered=False)
    t2 = time.time()
    print('time to save events: ' + str(t2 - t1))

    t_end = time.time()
    print('Total: ' + str(t_end - t_start))

    return log_id
