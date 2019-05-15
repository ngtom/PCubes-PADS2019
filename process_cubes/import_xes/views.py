from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
# Create your views here.

from pm4py.objects.log.importer.xes import factory as xes_importer
from django.http import HttpResponse
from .models import EventLog, import_xes
from dimension_editor.views import dimension_edit

import time


def upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        log_id = import_xes(filename, fs.path(filename))
        log = EventLog.objects.get(pk=log_id)

        return redirect(dimension_edit, pk=log_id)
    return render(request, 'import_xes/upload.html')

