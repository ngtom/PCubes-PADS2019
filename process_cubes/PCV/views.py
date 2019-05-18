from django.shortcuts import render

from import_xes.models import EventLog, Dimension, Attribute, ProcessCube

# Create your views here.


def createPCV(request, log_id, cube_id):
    log = EventLog.objects.get(pk=log_id)
    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)

    #return redirect(dimension_edit, pk=log_id)

    return render(request, 'pcv/pcv.html',
                  {
                      'log': log,
                      'dimensions': dimensions,
                      #'attributes': attr_names
                  })
