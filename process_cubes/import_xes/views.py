from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
# Create your views here.

from pm4py.objects.log.importer.xes import factory as xes_importer
from django.http import HttpResponse
from .models import EventLog, import_xes

import time




def upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        import_xes(filename, fs.path(filename))

        return render(request, 'import_xes/upload.html')
    return render(request, 'import_xes/upload.html')
