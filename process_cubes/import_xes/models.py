from djongo import models

# Create your models here.
# Not the final Models. Just to try out
class EventLog(models.Model):
    name = models.CharField(max_length=255)
    xes_file = models.FileField(upload_to='documents/')


class Trace(models.Model):
    event_log = models.EmbeddedModelField(model_container=EventLog)


class Event(models.Model):
    trace = models.EmbeddedModelField(model_container=Trace)


class Attribute(models.Model):
    name = models.CharField(max_length=255)
    event_log = models.EmbeddedModelField(model_container=EventLog)
    parent = models.CharField(max_length=255)


