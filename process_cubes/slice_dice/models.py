from django.db import models
from import_xes.models import EventLog, Dimension, Attribute, ProcessCube



# Create your models here.

class Slice(models.Model):
    element = models.CharField(max_length=255)
    attribute = models.CharField(max_length=255)
    dimension = models.ForeignKey(Dimension, null=True, on_delete=models.SET_NULL, verbose_name="the sliced dimension")