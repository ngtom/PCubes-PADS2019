from django.shortcuts import render

# Create your views here.


def slice_operation(request, pk):
    log = EventLog.objects.get(pk=pk)
    

def dice_operation(request, pk):
    log = EventLog.objects.get(pk=pk)
    