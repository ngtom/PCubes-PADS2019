from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from operator import mul
from functools import reduce

from import_xes.models import EventLog, Dimension, Attribute, ProcessCube

# Create your views here.


def createPCV(request, log_id, cube_id):
    log = EventLog.objects.get(pk=log_id)
    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)

    attributes = Attribute.objects.filter(log=log)
    used_attributes = [attr for dim in dimensions for attr in dim.attributes.all()]
    free_attributes = [attr for attr in attributes if attr not in used_attributes]

    for dim in dimensions:
        if(len(dim.attributes.all()) != 0):
            dim.num_elements = reduce(
                mul, [len(attr.values) for attr in dim.attributes.all()], 1)


    logs = EventLog.objects.all()

    return render(request, 'pcv/pcv.html',
                  {
                      'cube': cube,
                      'logs': logs,
                      'log': log,
                      'dimensions': dimensions,
                      'attributes': attributes,
                      'free_attributes': free_attributes
                  })
