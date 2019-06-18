from djongo import models
from import_xes.models import Attribute, Dimension

class NumericalHierarchy(models.Model):
    attribute = models.ForeignKey(to=Attribute, on_delete=models.CASCADE, related_name='num_hierarchy')
    dimension = models.ForeignKey(to=Dimension, on_delete=models.CASCADE, related_name='num_hierarchy')
    step_size = models.FloatField()

class DateHierarchy(models.Model):
    attribute = models.ForeignKey(to=Attribute, on_delete=models.CASCADE, related_name='date_hierarchy')
    dimension = models.ForeignKey(to=Dimension, on_delete=models.CASCADE, related_name='date_hierarchy')
    step_size = models.IntegerField()