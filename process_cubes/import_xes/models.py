from djongo import models
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.filtering.log.variants import variants_filter
from pymongo import MongoClient
from process_cubes.settings import DATABASES

import os
import time


class EventLog(models.Model):
    name = models.CharField(max_length=255)
    xes_file = models.FileField(upload_to='documents/')


class Attribute(models.Model):
    name = models.CharField(max_length=255)
    parent = models.CharField(max_length=32)# to distinguish trace and event
    log = models.ForeignKey(to=EventLog, on_delete=models.CASCADE)
    values = models.ListField(null=True)


class Dimension(models.Model):
    name = models.CharField(max_length=255)
    log = models.ForeignKey(to=EventLog, on_delete=models.CASCADE)
    attributes = models.ArrayReferenceField(to=Attribute, on_delete=models.CASCADE, null=True)


class ProcessCube(models.Model):
    log = models.ForeignKey(to=EventLog, on_delete=models.CASCADE)
    dimensions = models.ArrayReferenceField(to=Dimension, on_delete=models.CASCADE)

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
    log = xes_importer.import_log(xes_file)
    t2 = time.time()
    print('xes_importer.import_log: ' + str(t2 - t1))
    # delete file after import?
    # os.remove(xes_file)

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

    Attribute.objects.bulk_create(all_attributes)

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
    event_collection.insert_many(all_events, ordered=False)
    t2 = time.time()
    print('time to save events: ' + str(t2 - t1))

    t_end = time.time()
    print('Total: ' + str(t_end - t_start))

    return log_id
