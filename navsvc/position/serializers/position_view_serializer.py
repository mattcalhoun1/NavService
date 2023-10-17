from rest_framework import serializers
from position.models import Lidar,PositionLog, PositionLogEntry, PositionView, NavMap, Vehicle, NavModel, Assignment, LANGUAGE_CHOICES, STYLE_CHOICES
import logging
from helpers.postgres_helper import PostgresHelper
import json
import base64
from position.serializers.serializer_base import SerializerBase

class PositionViewSerializer(SerializerBase):
    vehicle_id = serializers.CharField(required=True, allow_blank=False, max_length=32)
    entry_num = serializers.IntegerField(required=False)
    session_id = serializers.CharField(required=True, allow_blank=False, max_length=64)
    camera_id = serializers.CharField(required=True, allow_blank=False, max_length=32)
    camera_angle = serializers.FloatField()
    image_format = serializers.CharField(required=True, allow_blank=False, max_length=4)
    encoded_image = serializers.CharField()

    def get_all_matching (self, vehicle_id, session_id):
        entries = []
        query = ''.join([
            "SELECT entry_num, camera_id, camera_angle, image_format ",
            " FROM nav.position_views ",
            " WHERE vehicle_id =  %s and session_id = %s "
        ])
        params = (vehicle_id, session_id)
        query = query + " ORDER BY entry_num asc"

        db = self.get_db()
        db.get_cursor('q').execute(query,params)
        while True:
            row = db.get_cursor('q').fetchone()
            if row is None:
                break   

            entries.append(PositionView(
                vehicle_id = vehicle_id,
                session_id = session_id,
                entry_num = row[0],
                camera_id = row[1],
                camera_angle = row[2],
                image_format = row[3]
            ))

        db.close_cursor('q')
        return entries
    
    def get_position_image (self, vehicle_id, entry_num, camera_id):
        entries = []
        query = ''.join([
            "SELECT encoded_image ",
            " FROM nav.position_views ",
            " WHERE vehicle_id =  %s and entry_num = %s and camera_id = %s "
        ])
        params = (vehicle_id, entry_num, camera_id)

        db = self.get_db()
        db.get_cursor('q').execute(query,params)
        row = db.get_cursor('q').fetchone()
        encoded_image = None
        if row is not None:
            raw_image = row[0]
            encoded_image = base64.b64encode(raw_image).decode('utf-8')

        db.close_cursor('q')
        return encoded_image


    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        #logging.getLogger(__name__).info(f"Creating position log entry: {validated_data}")

        #plog = PositionLogEntry.objects.create(**validated_data)
        position_view = PositionView()
        position_view.vehicle_id = validated_data.get('vehicle_id')
        position_view.entry_num = validated_data.get('entry_num')
        position_view.session_id = validated_data.get('session_id')
        position_view.camera_id = validated_data.get('camera_id')
        position_view.camera_angle = validated_data.get('camera_angle')
        position_view.image_format = validated_data.get('image_format')
        position_view.encoded_image = validated_data.get('encoded_image')

        self.__add_position_view(position_view=position_view)
        return position_view

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        logging.getLogger(__name__).info(f"Updating log has no effect: {validated_data}")
        return instance
    
    def __add_position_view (self, position_view : PositionView, db = None):
        logging.getLogger(__name__).info(f"Saving position view to postgres for: {position_view.vehicle_id}")
        
        sql = ''.join([
            "INSERT INTO nav.position_views ",
            " (vehicle_id, entry_num, session_id, camera_id, camera_angle, image_format, encoded_image) ",
            " VALUES (%s, %s, %s, %s, %s, %s, %s) ",
            " ON CONFLICT (vehicle_id, entry_num, camera_id) ",
            "   DO UPDATE SET encoded_image = EXCLUDED.encoded_image, camera_angle = EXCLUDED.camera_angle, ",
            "   image_format = EXCLUDED.image_format "
        ])
        params = (
            position_view.vehicle_id,
            position_view.entry_num,
            position_view.session_id,
            position_view.camera_id,
            position_view.camera_angle,
            position_view.image_format,
            base64.b64decode(position_view.encoded_image)
        )

        db = self.get_db()
        db.get_cursor('u').execute(sql,params)
        db.commit()
        db.close_cursor('u')
