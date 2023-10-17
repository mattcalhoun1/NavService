from rest_framework import serializers
from position.models import Lidar,PositionLog, PositionLogEntry, PositionView, NavMap, Vehicle, NavModel, Assignment, LANGUAGE_CHOICES, STYLE_CHOICES
import logging
from helpers.postgres_helper import PostgresHelper
import json
import base64
from position.serializers.serializer_base import SerializerBase

class VehicleSerializer(SerializerBase):
    vehicle_id = serializers.CharField(max_length=128)
    name = serializers.CharField(max_length=128)

    def get_all_vehicles (self, max_vehicles=10):
        entries = []
        query = ''.join([
            "SELECT "
            " distinct (top.vehicle_id) as vehicle_id, ",
            " (SELECT MAX(l.occurred) from nav.position_log l where l.vehicle_id = top.vehicle_id) as latest "
            " FROM nav.position_log top ",
            " INNER JOIN nav.vehicles v ON v.vehicle_id = top.vehicle_id and v.is_active = true "
            " ORDER BY latest desc ",
            "LIMIT %s"
        ])
        params = (max_vehicles,)

        db = self.get_db()
        db.get_cursor('q').execute(query,params)
        while True:
            row = db.get_cursor('q').fetchone()
            if row is None:
                break   

            entries.append({
                "vehicle_id": row[0],
                "last_activity": row[1]
            })

        db.close_cursor('q')
        return entries


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