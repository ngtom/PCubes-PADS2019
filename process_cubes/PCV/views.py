from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from import_xes.models import EventLog, Dimension, Attribute, ProcessCube

# Create your views here.


def createPCV(request, log_id, cube_id):
    log = EventLog.objects.get(pk=log_id)
    cube = ProcessCube.objects.get(pk=cube_id)
    dimensions = Dimension.objects.filter(cube=cube)

 
    #todo: hookup
    #return redirect(dimension_edit, pk=log_id)
    #if(request.POST.get('pcv_edit')):
    #    return HttpResponseRedirect(reverse('dimension_edit',args=(pk,)))

    return render(request, 'pcv/pcv.html',
                  {
                      'log': log,
                      'dimensions': dimensions,
                      #'attributes': attr_names
                  })
