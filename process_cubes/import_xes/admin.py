from django.contrib import admin
from .models import EventLog, Event, Attribute

# Register your models here.

myModels = [EventLog, Attribute, Event]  # iterable list

admin.site.register(myModels)