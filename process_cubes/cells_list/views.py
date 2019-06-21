from django.shortcuts import render
from import_xes.models import Attribute, Dimension, ProcessCube, EventLog
from dimension_editor.models import DateHierarchy, NumericalHierarchy
from itertools import product, chain
from slice_dice.models import Slice, Dice
from bson.json_util import dumps
from django.http import JsonResponse, HttpResponse
import json
from pymongo import MongoClient
from process_cubes.settings import DATABASES
from datetime import datetime
import math


##
from pm4py.objects import log as log_lib
from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.visualization.process_tree import factory as pt_vis_factory
from pm4py.algo.discovery.heuristics import factory as heuristics_miner
from pm4py.visualization.heuristics_net import factory as hn_vis_factory
#


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

            step = int(step)
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


    algo = request.POST.get("algorithm")
    print(algo)

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

    client = MongoClient(host=DATABASES['default']['HOST'])
    db = client[DATABASES['default']['NAME']]
    trace_collection = db['traces']
    event_collection = db['events']

    events = event_collection.find(values)
    events = list(events)

    pm_events = []
    traces = {str(e['trace:_id']): log_lib.log.Trace() for e in events}

    for event in events:
        trace = trace_collection.find_one({"_id": event['trace:_id']})

        t = traces[str(event['trace:_id'])]
        del event['_id']
        del event['trace:_id']

        e = log_lib.log.Event(event)
        t.append(e)

    log = log_lib.log.EventLog()
    for trace in traces:
        log.append(traces[trace])

    parameters = {"format": "svg"}

    event_log = EventLog.objects.get(pk=log_id)
    filename = str(event_log.pk) + algo + ".svg"

    if(algo == "alpha"):
        net, initial_marking, final_marking = alpha_miner.apply(log)
        gviz = pn_vis_factory.apply(
            net, initial_marking, final_marking, parameters=parameters)
        pn_vis_factory.save(gviz, filename)
    elif(algo == "inductive"):
        mine_tree = request.POST.get("mine_tree")
        print(mine_tree)
        if(mine_tree == 'true'):
            tree = inductive_miner.apply_tree(log)
            gviz = pt_vis_factory.apply(tree, parameters=parameters)
            pt_vis_factory.save(gviz, filename)
        else:
            net, initial_marking, final_marking = inductive_miner.apply(log)
            gviz = pn_vis_factory.apply(
                net, initial_marking, final_marking, parameters=parameters)
            pn_vis_factory.save(gviz, filename)
    elif(algo == "heuristic"):

        dependency_thresh = float(request.POST.get("dependency_thresh"))
        and_measure_thresh = float(request.POST.get("and_measure_thresh"))
        min_act_count = float(request.POST.get("min_act_count"))
        min_dfg_occurrences = float(request.POST.get("min_dfg_occurrences"))
        dfg_pre_cleaning_noise_thresh = float(request.POST.get("dfg_pre_cleaning_noise_thresh"))

        h_params = {'dependency_thresh': dependency_thresh,
                    'and_measure_thresh': and_measure_thresh,
                    'min_act_count': min_act_count,
                    'min_dfg_occurrences': min_dfg_occurrences,
                    'dfg_pre_cleaning_noise_thresh': dfg_pre_cleaning_noise_thresh,
                    }
        
        print(h_params)

        heu_net = heuristics_miner.apply_heu(
            log, parameters=h_params)
        gviz = hn_vis_factory.apply(heu_net, parameters=parameters)
        hn_vis_factory.save(gviz, filename)

    svg = open(filename, "rb")

    # TODO: delete file when it's not required anymore
    return HttpResponse(svg.read(), content_type="image/svg+xml")
