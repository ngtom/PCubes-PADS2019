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
from datetime import datetime
import math

class EventLog(models.Model):
    name = models.CharField(max_length=255)


class ProcessCube(models.Model):
    name = models.CharField(max_length=255)
    log = models.ForeignKey(to=EventLog, on_delete=models.CASCADE)

    def get_num_cells(self):
        num = 1

        for dim in self.dimensions.all():
            elements = dim.get_num_elements()
            num = num * elements

        return num

class Attribute(models.Model):
    name = models.CharField(max_length=255)
    parent = models.CharField(max_length=32)  # to distinguish trace and event
    log = models.ForeignKey(to=EventLog, on_delete=models.CASCADE)
    values = models.ListField(null=True)
    dtype = models.CharField(max_length=10)

    # Returns the name that is used in events collection 
    def get_name(self):
        if(self.parent == "trace"):
            return self.parent + ":" + self.name
        else:
            return self.name

class Dimension(models.Model):
    name = models.CharField(max_length=255)
    # log = models.ForeignKey(to=EventLog, on_delete=models.CASCADE)
    cube = models.ForeignKey(to=ProcessCube, on_delete=models.CASCADE, related_name="dimensions")
    attributes = models.ArrayReferenceField(to=Attribute)

    def get_num_elements(self):
        num = 1
        for attr in self.attributes.all():
            step = 1

            if(attr.dtype == 'float' or attr.dtype == 'int'):
                hierarchy = self.num_hierarchy.filter(attribute=attr)
                if(hierarchy.exists()):
                    step = hierarchy[0].step_size
                else:
                    step = 1
            elif(attr.dtype == 'date'):
                hierarchy = self.date_hierarchy.filter(attribute=attr)
                if(hierarchy.exists()):
                    step = hierarchy[0].step_size
                else:
                    step = 1
            
            num_values = len(attr.values)

            num = num * math.ceil(num_values / step)

        return num


# Pymongo is used directly to import events, because with Django models it's very slow for large files
# and I found no way to realize Models with "dynamic fields"


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def import_xes(filename, xes_file):
    t_start = time.time()

    # TODO: maybe not the best way to connect to the db
    client = MongoClient(host=DATABASES['default']['HOST'])
    db = client[DATABASES['default']['NAME']]
    trace_collection = db['traces']
    event_collection = db['events']

    t1 = time.time()
    # raw log from file
    log = xes_importer.import_log(xes_file)
    t2 = time.time()
    print('xes_importer.import_log: ' + str(t2 - t1))
    # delete file after import?
    # os.remove(xes_file)

    # Get name log log, if specified
    if('concept:name' in log.attributes):
        log_name = filename + ': ' + log.attributes['concept:name']
    else:
        log_name = filename

    # Construct event log object
    event_log = EventLog(name=log_name)
    event_log.save()
    log_id = event_log.id

    # Helper Functions

    def add_log_id(trace):
        trace['log'] = log_id
        return trace

    def add_trace_attrs(e, trace):
        for tattr in trace:
            if tattr != 'log':
                e['trace:' + tattr] = trace[tattr]

        e['log'] = log_id
        return e
    # --------

    # Collect all attributes
    t1 = time.time()
    event_attributes = {
        attr for trace in log for event in trace for (attr, v) in event.items() if type(v) is not dict}

    trace_attributes = {attr for trace in log for (
        attr, v) in trace.attributes.items() if type(v) is not dict}

    # Dict attributes, make each key of the dict to an attribute
    event_attributes2 = {(k, k2) for trace in log for event in trace for (
        k, v) in event.items() if type(v) == dict for (k2, v2) in v['children'].items()}
    trace_attributes2 = {(k, k2) for trace in log for k, v in trace.attributes.items(
    ) if type(v) == dict for (k2, v2) in v['children'].items()}

    t2 = time.time()
    print('time to find all attributes list: ' + str(t2 - t1))
    # ---------------

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

    

    # Helper functions to find all possible values of the attributes
    def find_values(attr):
        values = {event[attr] for event in all_events if attr in event}
        return list(values)

    # Values of attribute with parent (trace)
    def find_values_p(attr, parent):
        return find_values(parent + ":" + attr)

    # Values of dictionary attribute
    def find_values_d(attr, d_name):
        values = {event[d_name]['children'][attr]
                  for event in all_events if d_name in event if attr in event[d_name]['children']}
        return list(values)

    # Values of dictionary attribute with given parent
    def find_values_d_p(attr, parent, d_name):
        d_name = parent + ":" + d_name
        return find_values_d(attr, d_name)
    # -------------

    # Construct Attribute objects and collect all possible values
    t1 = time.time()
    all_attributes = [Attribute(name=attr, parent='event', log=event_log, values=find_values(attr)) for attr in event_attributes] + [
        Attribute(name=attr, parent='trace', log=event_log, values=find_values_p(attr, 'trace')) for attr in trace_attributes] + [
        Attribute(name=k2, parent='trace:' + k, log=event_log, values=find_values_d_p(k2, 'trace', k)) for (k, k2) in trace_attributes2] + [
        Attribute(name=k2, parent='event:' + k, log=event_log, values=find_values_d(k2, k)) for (k, k2) in event_attributes2]

    for attr in all_attributes:
        if(type(attr.values[0]) == datetime):
            attr.dtype = "date"
        elif(type(attr.values[0]) == str):
            if(is_number(attr.values[0])):
                attr.dtype = "float"
                for ev in all_events:
                    ev[attr.get_name()] = float(ev[attr.get_name()])
                attr.values = list(map(float, attr.values))
            else:
                attr.dtype = "str"
        elif(type(attr.values[0]) == int):
            attr.dtype = "int"
        elif(type(attr.values[0]) == float):
            attr.dtype = "float"
        elif(type(attr.values[0]) == bool):
            attr.dtype = "bool"
        else:
            attr.dtype = "str"


    t2 = time.time()
    print('time to get values of attributes: ' + str(t2 - t1))
    # ---------------

    # Save events
    t1 = time.time()
    event_collection.insert_many(all_events, ordered=False)
    t2 = time.time()
    print('time to save events: ' + str(t2 - t1))

    print('#Traces: ' + str(len(all_traces)))
    print('#Events: ' + str(len(all_events)))
    # ----------------

    # This method inserts the provided list of objects into the database in an efficient manner
    Attribute.objects.bulk_create(all_attributes)

    t_end = time.time()
    print('Total: ' + str(t_end - t_start))

    # Delete file, not used anymore
    os.remove(filename)

    return log_id
