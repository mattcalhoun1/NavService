from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])

class NavMap(models.Model):
    map_id = models.CharField(max_length=32)
    content = models.JSONField()
    map_desc = models.CharField(max_length=128)

    class Meta:
        ordering = ['map_id']

class NavModel(models.Model):
    model_id = models.CharField(max_length=32)
    model_type = models.CharField(max_length=32)
    model_format = models.CharField(max_length=32)
    additional_params = models.JSONField()
    encoded_model = models.TextField()

    class Meta:
        ordering = ['model_id']

class Vehicle(models.Model):
    vehicle_id = models.CharField(max_length=32)
    name = models.CharField(max_length=64)

class PositionLogEntry(models.Model):
    entry_num = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    occurred = models.DateTimeField(auto_now_add=True)
    position_x = models.FloatField()
    position_y = models.FloatField()
    navmap_id = models.CharField(max_length=32)
    vehicle_id = models.CharField(max_length=32)
    session_id = models.CharField(max_length=64)
    ordering = ['occurred']

class PositionLog(models.Model):
    vehicle_id = Vehicle()
    start = models.DateTimeField()
    end = models.DateTimeField()
    entries = []

class PositionView(models.Model):
    vehicle_id = models.CharField(max_length=32)
    session_id = models.CharField(max_length=64)
    entry_num = models.IntegerField()
    camera_id = models.CharField(max_length=32)
    camera_angle = models.FloatField()
    image_format = models.CharField(max_length=4)
    encoded_image = models.CharField(max_length=102400000)


