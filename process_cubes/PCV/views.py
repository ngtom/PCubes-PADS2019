from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from import_xes.models import EventLog, Dimension, Attribute

# Create your views here.


def createPCV(request, pk):
    log = EventLog.objects.get(pk=pk)
    dimensions = Dimension.objects.filter(log=log)
    #attributes = Attribute.objects.filter(log=log)

 
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
