from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from operator import mul
from functools import reduce
import json
from django.core.serializers.json import DjangoJSONEncoder

from import_xes.models import EventLog, Dimension, Attribute, ProcessCube
from slice_dice.models import Slice, Dice

# Create your views here.


def createPCV(request, log_id, cube_id):
    log = EventLog.objects.get(pk=log_id)
    cube = ProcessCube.objects.get(pk=cube_id)
    cubes = ProcessCube.objects.filter(log=log_id)
    dimensions = Dimension.objects.filter(cube=cube)
    
    dices = {}
    slices = {}
    
    for dim in dimensions:
        if Dice.objects.filter(dimension = dim).exists():
            dices['' + str(dim.pk)] = True
        else: 
            dices['' + str(dim.pk)] = False
        if Slice.objects.filter(dimension = dim).exists():
            slices['' + str(dim.pk)] = True
        else: 
            slices['' + str(dim.pk)] = False
    
    dices = json.dumps(dices)
    slices = json.dumps(slices)

    attributes = Attribute.objects.filter(log=log)
    used_attributes = [attr for dim in dimensions for attr in dim.attributes.all()]
    free_attributes = [attr for attr in attributes if attr not in used_attributes]


    logs = EventLog.objects.all()

    return render(request, 'pcv/pcv.html',
                  {
                      'cube': cube,
                      'logs': logs,
                      'cubes': cubes,
                      'log': log,
                      'dimensions': dimensions,
                      'attributes': attributes,
                      'free_attributes': free_attributes,
                      'slices': slices,
                      'dices': dices
                  })
