from django.contrib import admin
from .models import EventLog

# Register your models here.

myModels = [EventLog]
admin.site.register(myModels)