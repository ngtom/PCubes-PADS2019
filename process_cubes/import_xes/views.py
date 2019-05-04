from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
# Create your views here.

from pm4py.objects.log.importer.xes import factory as xes_importer
from django.http import HttpResponse
from .models import EventLog, Attribute


def home(request):
    eventlogs = EventLog.objects.all()
    return render(request, 'import_xes/home.html', {'logs': eventlogs})


def upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        import_xes(filename, fs.path(filename))


        return render(request, 'import_xes/upload.html')
    return render(request, 'import_xes/upload.html')

def import_xes(xes_file, filename):
    log = xes_importer.import_log(xes_file)

    event_log = EventLog(name=filename, xes_file=xes_file)
    event_log.save()

    trace_attributes = log[0].attributes
    for attr in trace_attributes:
        attribute = Attribute(
            name=attr, event_log=event_log, parent='trace')
        attribute.save()

    for attr in log[0][0]:
        attribute = Attribute(
            name=attr, event_log=event_log, parent='event')
        attribute.save()
