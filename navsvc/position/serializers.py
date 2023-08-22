from rest_framework import serializers
from position.models import PositionLog, PositionLogEntry, NavMap, Vehicle, LANGUAGE_CHOICES, STYLE_CHOICES
import logging

class VehicleSerializer(serializers.Serializer):
    vehicle_id = serializers.CharField(max_length=128)
    name = serializers.CharField(max_length=128)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        logging.getLogger(__name__).info(f"Creating vehicle: {validated_data}")
        vehicle = Vehicle.objects.create(**validated_data)
        return vehicle

    def update(self, instance, validated_data):
        """
        Update and return an existing `Vehicle` instance, given the validated data.
        """
        logging.getLogger(__name__).info(f"Updating vehicle: {validated_data}")
        instance.vehicle_id = validated_data.get('vehicle_id', instance.vehicle_id)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

class PositionLogEntrySerializer(serializers.Serializer):
    occurred = serializers.DateTimeField()
    vehicle_id = serializers.CharField(required=True, allow_blank=False, max_length=100)
    created = serializers.DateTimeField()
    position_x = serializers.FloatField(required=True)
    position_y = serializers.FloatField(required=True)
    navmap_id = serializers.CharField(required=True, allow_blank=False, max_length=100)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        logging.getLogger(__name__).info(f"Creating position log entry: {validated_data}")
        #plog = PositionLogEntry.objects.create(**validated_data)
        plog = PositionLogEntry()
        plog.occurred = validated_data.get('occurred')
        plog.vehicle_id = validated_data.get('vehicle_id')
        plog.created = validated_data.get('created')
        plog.position_x = validated_data.get('position_x')
        plog.position_y = validated_data.get('position_y')
        plog.navmap_id = validated_data.get('navmap_id')
        return plog

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        logging.getLogger(__name__).info(f"Saving position log: {validated_data}")

        instance.occurred = validated_data.get('occurred', instance.occurred)
        instance.vehicle_id = validated_data.get('vehicle_id', instance.vehicle_id)
        instance.created = validated_data.get('created', instance.created)
        instance.position_x = validated_data.get('position_x', instance.position_x)
        instance.position_y = validated_data.get('position_y', instance.position_y)
        instance.navmap_id = validated_data.get('navmap_id', instance.navmap_id)
        return instance
    
class PositionLogSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    code = serializers.CharField(style={'base_template': 'textarea.html'})
    linenos = serializers.BooleanField(required=False)
    language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default='python')
    style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        logging.getLogger(__name__).info(f"Creating position log: {validated_data}")
        plog = PositionLog.objects.create(**validated_data)
        return plog

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        logging.getLogger(__name__).info(f"Saving position log: {validated_data}")
        #instance.title = validated_data.get('title', instance.title)
        #instance.code = validated_data.get('code', instance.code)
        #instance.linenos = validated_data.get('linenos', instance.linenos)
        #instance.language = validated_data.get('language', instance.language)
        #instance.style = validated_data.get('style', instance.style)
        #instance.save()
        return instance