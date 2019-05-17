from django.shortcuts import render

from import_xes.models import EventLog, Dimension, Attribute

# Create your views here.


def createPCV(request, pk):
    log = EventLog.objects.get(pk=pk)
    dimensions = Dimension.objects.filter(log=log)

    #return redirect(dimension_edit, pk=log_id)

    return render(request, 'pcv/pcv.html',
                  {
                      'log': log,
                      'dimensions': dimensions,
                      #'attributes': attr_names
                  })
