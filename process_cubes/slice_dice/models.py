from djongo import models
from import_xes.models import EventLog, ProcessCube, Dimension, Attribute

# Create your models here.


class AttributeRestriction(models.Model):
    attribute = models.ForeignKey(to=Attribute, on_delete=models.CASCADE)
    value = models.CharField()

    class Meta:
        abstract = True

class DimensionRestriction(models.Model):
    values = models.ArrayModelField(model_container=AttributeRestriction)

    class Meta:
        abstract = True

class Slice(models.Model):
    dimension = models.ForeignKey(to=Dimension, on_delete=models.CASCADE)
    values = models.ArrayModelField(model_container=DimensionRestriction)
