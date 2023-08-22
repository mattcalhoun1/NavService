from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])

class NavMap(models.Model):
    map_id = models.CharField(max_length=128)
    content = models.JSONField()

    class Meta:
        ordering = ['map_id']

class Vehicle(models.Model):
    vehicle_id = models.CharField(max_length=128)
    name = models.CharField(max_length=128)

class PositionLogEntry(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    occurred = models.DateTimeField(auto_now_add=True)
    position_x = models.FloatField()
    position_y = models.FloatField()
    navmap_id = models.CharField(max_length=128)
    vehicle_id = models.CharField(max_length=128)
    ordering = ['occurred']

class PositionLog(models.Model):
    vehicle_id = Vehicle()
    start = models.DateTimeField()
    end = models.DateTimeField()
    entries = []

