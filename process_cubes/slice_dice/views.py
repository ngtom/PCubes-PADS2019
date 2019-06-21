from django.shortcuts import render, redirect
import json
from django.core.serializers.json import DjangoJSONEncoder
import numbers
from import_xes.models import EventLog, Attribute, ProcessCube, Dimension
from django.http import HttpResponse
from .models import AttributeRestriction, Slice, Dice, DimensionRestriction
from .forms import DateFilter, NumberFilter, StringFilter
import datetime
from cells_list.views import get_dim_values
from PCV.views import createPCV
# Create your views here.

def make_name(a):
    name = a.name
    if(a.parent != 'event'):
        name = a.parent + ':' + name

    return name

def operation(request, log_id, cube_id, dim_id, page):
    logs = EventLog.objects.all()

    log = EventLog.objects.get(pk=log_id)
    cube = ProcessCube.objects.get(pk=cube_id)
    cubes = ProcessCube.objects.filter(log=log)
    attributes = Attribute.objects.filter(log=log)
    dim = Dimension.objects.get(pk=dim_id)

    filters = []

    for attr in dim.attributes.all():
        if(isinstance(attr.values[0], (int, float))):
            filter_form = NumberFilter()
        elif(isinstance(attr.values[0], datetime.datetime)):
            filter_form = DateFilter()
        else:
            filter_form = StringFilter()
                
        filter_form.attribute = attr
        filters.append(filter_form)

    attr_names = [make_name(a) for a in dim.attributes.all()]

    dim_values = get_dim_values(dim)
    dim_values = [[str(v) for v in values] for values in dim_values]

    dim_values = [[''] + row for row in dim_values]

    json_dice = []

    if Dice.objects.filter(dimension = dim).exists():
        dice = Dice.objects.filter(dimension = dim)[0]
        for dim_res in dice.values:
            restr = []
            for attr_res in dim_res.values:
                restr.append(attr_res.value)
            json_dice.append(restr)

    json_slice = []

    if Slice.objects.filter(dimension = dim).exists():
        sli = Slice.objects.filter(dimension = dim)[0]
        for attr_res in sli.value.values:
            json_slice.append(attr_res.value)

        
    return render(request, page, {
        'logs': logs,
        'log': log,
        'cube': cube,
        'cubes': cubes,
        'attributes': attributes,
        'dimension': dim,
        'attr_names': attr_names,
        'filters': filters,
        'dim_values': dim_values,
        'dice': json_dice,
        'slice': json_slice})

def slice_operation(request, log_id, cube_id, dim_id):
    return operation(request, log_id, cube_id, dim_id, 'slice_dice/slice.html')

def dice_operation(request, log_id, cube_id, dim_id):
    return operation(request, log_id, cube_id, dim_id, 'slice_dice/dice.html')


def save_dice(request, log_id, cube_id, dim_id):

    dim = Dimension.objects.get(pk=dim_id)
    
    if Dice.objects.filter(dimension = dim).exists():
       Dice.objects.filter(dimension = dim).delete()

    if Slice.objects.filter(dimension=dim).exists():
       Slice.objects.filter(dimension = dim).delete()

    dimension = Dimension.objects.get(pk=dim_id)
    values = request.POST.getlist("values[]")

    values_dict = []
    attributes = {make_name(attr): attr for attr in dimension.attributes.all()}

    for vs_json in values:
        vs = json.loads(vs_json)
        
        restr = {}
        for i, attr in enumerate(dimension.attributes.all()):
            restr[make_name(attr)] =  vs[i]

        values_dict.append(restr)
        
    
    dim_values = []
    for value_restr in values_dict:
        attr_restrictions = []
        for attr in value_restr:
            attribute = attributes[attr]
            value = value_restr[attr]
            restr = AttributeRestriction(attribute=attribute, value=value)
            attr_restrictions.append(restr)

        dim_restr = DimensionRestriction(values=attr_restrictions)
        dim_values.append(dim_restr)

    dice_obj = Dice(dimension=dimension, values=dim_values)
    dice_obj.save()

    return redirect(createPCV, log_id, cube_id)


def save_slice(request, log_id, cube_id, dim_id):
    dimension = Dimension.objects.get(pk=dim_id)

    if Dice.objects.filter(dimension = dimension).exists():
       Dice.objects.filter(dimension = dimension).delete()

    if Slice.objects.filter(dimension= dimension).exists():
       Slice.objects.filter(dimension = dimension).delete()

    values = request.POST.get("values")

    attributes = {make_name(attr): attr for attr in dimension.attributes.all()}


    vs = json.loads(values)
    value_restr = {}
    for i, attr in enumerate(dimension.attributes.all()):
        value_restr[make_name(attr)] =  vs[i]

        
    
    attr_restrictions = []
    for attr in value_restr:
        attribute = attributes[attr]
        value = value_restr[attr]
        restr = AttributeRestriction(attribute=attribute, value=value)
        attr_restrictions.append(restr)

    dim_restr = DimensionRestriction(values=attr_restrictions)

    slice_obj = Slice(dimension=dimension, value=dim_restr)
    slice_obj.save()

    return redirect(createPCV, log_id, cube_id)


