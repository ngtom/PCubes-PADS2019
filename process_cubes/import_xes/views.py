from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
# Create your views here.

from pm4py.objects.log.importer.xes import factory as xes_importer
from django.http import HttpResponse
from .models import EventLog, import_xes, Attribute
from dimension_editor.views import dimension_edit
from process_cubes.views import log as log_view
from pymongo import MongoClient
from process_cubes.settings import DATABASES
from django.http import HttpResponse, JsonResponse
from bson.json_util import dumps


def upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        log_id = import_xes(filename, fs.path(filename))
        
        return redirect(log_view, log_id)
    return render(request, 'import_xes/upload.html')
        

def get_events(request, log_id):
    client = MongoClient(host=DATABASES['default']['HOST'])
    db = client[DATABASES['default']['NAME']]
    event_collection = db['events']

    def dump_dict(v):
        if(type(v) is dict):
            return dumps(v)
        else:
            return v

    def rem_id(e):
        e.pop("_id", "")
        if("time:timestamp" in e):
            e["time:timestamp"] = str(e["time:timestamp"])

        e1 = {k: e[k] for k in e if type(e[k]) is not dict}
        e1.update({(k1 + ":" + k2): e[k1]['children'][k2] for k1 in e if type(e[k1]) is dict for k2 in e[k1]['children']})
        print(e1)
        return e1

    events = event_collection.find({'log': log_id})
    events = [rem_id(e) for e in events]

    events_json = dumps({'data': events})
    return HttpResponse(events_json, content_type='application/json')


def get_attrs(request, log_id):
    log = EventLog.objects.get(pk=log_id)
    attributes = Attribute.objects.filter(log=log)

    def attr(attribute):
        if(attribute.parent != 'event'):
            name = attribute.parent + ':' + attribute.name
        else:
            name = attribute.name
        return name

    attributes = [{'data': attr(a)} for a in attributes]

    # return HttpResponse(attributes, content_type='application/json')
    return JsonResponse(attributes, safe=False)
