from rest_framework import serializers
from position.models import Lidar,PositionLog, PositionLogEntry, PositionView, NavMap, Vehicle, NavModel, Assignment, SearchHit, LANGUAGE_CHOICES, STYLE_CHOICES
import logging
from helpers.postgres_helper import PostgresHelper
import json
import base64
from position.serializers.serializer_base import SerializerBase

class SearchHitsSerializer(SerializerBase):
    object_type = serializers.CharField(required=True, allow_blank=False, max_length=32)
    map_id = serializers.CharField(max_length=32)
    entry_num = serializers.IntegerField(required=False)
    occurred = serializers.DateTimeField(required=False)
    est_visual_dist = serializers.FloatField(required=True)
    est_lidar_dist = serializers.FloatField(required=False)
    vehicle_relative_heading = serializers.FloatField(required=False)
    est_x = serializers.FloatField(required=True)
    est_y = serializers.FloatField(required=True)
    vehicle_x = serializers.FloatField(required=True)
    vehicle_y = serializers.FloatField(required=True)
    vehicle_heading = serializers.FloatField(required=True)
    confidence = serializers.FloatField(required=True)
    vehicle_id = serializers.CharField(required=True, allow_blank=False, max_length=32)
    session_id = serializers.CharField(required=True, allow_blank=False, max_length=64)
    camera_id = serializers.CharField(required=True, allow_blank=False, max_length=32)
    camera_angle = serializers.FloatField()
    image_format = serializers.CharField(required=True, allow_blank=False, max_length=4)
    encoded_image = serializers.CharField()

    def get_all_matching (self, vehicle_id, session_id):
        entries = []
        query = ''.join([
            "SELECT object_type, map_id, entry_num, occurred, ",
            " est_visual_distance, est_lidar_dist, vehicle_relative_heading, ",
            " est_x, est_y, vehicle_x, vehicle_y, vehicle_heading, ",
            " confidence, camera_id, camera_angle, image_format ",
            " FROM nav.search_hits ",
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

            entries.append(SearchHit(
                object_type = row[0],
                map_id = row[1],
                entry_num = row[2],
                occurred = row[3],
                est_visual_dist = row[4],
                est_lidar_dist = row[5],
                vehicle_relative_heading = row[6],
                est_x = row[7],
                est_y = row[8],
                vehicle_x = row[9],
                vehicle_y = row[10],
                vehicle_heading = row[11],
                confidence = row[12],
                vehicle_id = vehicle_id,
                session_id = session_id,
                camera_id = row[13],
                camera_angle = row[14],
                image_format = row[15],
            ))

        db.close_cursor('q')
        return entries
    
    def get_search_image (self, object_type, map_id, entry_num):
        query = ''.join([
            "SELECT encoded_image ",
            " FROM nav.search_hits ",
            " WHERE object_type =  %s and map_id = %s and entry_num = %s "
        ])
        params = (object_type, map_id, entry_num)

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
        search_hit = SearchHit()

        search_hit.object_type = validated_data.get('object_type')
        search_hit.map_id = validated_data.get('map_id')
        search_hit.est_visual_dist = validated_data.get('est_visual_dist')
        search_hit.est_lidar_dist = validated_data.get('est_lidar_dist')
        search_hit.vehicle_relative_heading = validated_data.get('vehicle_relative_heading')
        search_hit.est_x = validated_data.get('est_x')
        search_hit.est_y = validated_data.get('est_y')
        search_hit.vehicle_x = validated_data.get('vehicle_x')
        search_hit.vehicle_y = validated_data.get('vehicle_y')
        search_hit.vehicle_heading = validated_data.get('vehicle_heading')
        search_hit.confidence = validated_data.get('confidence')
        search_hit.vehicle_id = validated_data.get('vehicle_id')
        search_hit.session_id = validated_data.get('session_id')
        search_hit.camera_id = validated_data.get('camera_id')
        search_hit.camera_angle = validated_data.get('camera_angle')
        search_hit.image_format = validated_data.get('image_format')
        search_hit.encoded_image = validated_data.get('encoded_image')

        self.__add_search_hit(search_hit=search_hit)
        return search_hit

    def update(self, instance, validated_data):
        logging.getLogger(__name__).info(f"Updating log has no effect: {validated_data}")
        return instance


    def __add_search_hit (self, search_hit : SearchHit, db = None):
        logging.getLogger(__name__).info(f"Saving search hit to postgres for: {search_hit.vehicle_id}")
        
        sql = ''.join([
            "INSERT INTO nav.search_hits ",
            " (",
            ','.join([
                'object_type',# VARCHAR(32), -- type identifier (ex: gazing_ball)
                'map_id',# VARCHAR(32), -- map on which the search occurred
                #'entry_num',# serial, 
                #'occurred timestamp',# DEFAULT now(),
                'est_visual_distance',# float, -- visual estimated distance (in)
                'est_lidar_dist',# float, -- if lidar measuremnt taken, mm distance from lidar
                'vehicle_relative_heading',# float, -- where the object appears relative to the vehicle
                'est_x',# float, -- estimated map x position of the object
                'est_y',# float, -- estimated map y position of the object
                'vehicle_x',# float, -- vehicle x position at the time of sighting
                'vehicle_y',# float, -- vehicle x position at the time of sighting
                'vehicle_heading',# float, -- vehicle heading at the time of sighting
                'confidence',# float, -- confidence 0 - 1.0 of the match
                'vehicle_id',# VARCHAR(32), -- vehicle that took the measurment
                'camera_id',# VARCHAR(32), -- ex: left, etc
                'session_id',# VARCHAR(64), -- session in which the sighting occurred
                'camera_angle',# float, -- 0 = front of vehicle, +90 directly left, etc
                'image_format',# VARCHAR(4), -- ex: png
                'encoded_image'
            ]),
            " ) ",
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ",
            " ON CONFLICT (object_type, map_id, entry_num) DO NOTHING"
        ])
        params = (
            search_hit.object_type,
            search_hit.map_id,
            search_hit.est_visual_dist,
            search_hit.est_lidar_dist,
            search_hit.vehicle_relative_heading,
            search_hit.est_x,
            search_hit.est_y,
            search_hit.vehicle_x,
            search_hit.vehicle_y,
            search_hit.vehicle_heading,
            search_hit.confidence,
            search_hit.vehicle_id,
            search_hit.camera_id,
            search_hit.session_id,
            search_hit.camera_angle,
            search_hit.image_format,
            base64.b64decode(search_hit.encoded_image)
        )

        db = self.get_db()
        db.get_cursor('u').execute(sql,params)
        db.commit()
        db.close_cursor('u')
