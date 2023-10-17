from rest_framework import serializers
from position.models import Lidar,PositionLog, PositionLogEntry, PositionView, NavMap, Vehicle, NavModel, Assignment, LANGUAGE_CHOICES, STYLE_CHOICES
import logging
from helpers.postgres_helper import PostgresHelper
import json
import base64
from position.serializers.serializer_base import SerializerBase

class LidarSerializer(SerializerBase):
    vehicle_id = serializers.CharField(required=True, allow_blank=False, max_length=32)
    entry_num = serializers.IntegerField(required=False)
    session_id = serializers.CharField(required=True, allow_blank=False, max_length=64)
    occurred = serializers.DateTimeField(required=False)
    lidar_data = serializers.JSONField(required=False)

    def get_all_matching (self, vehicle_id, session_id):
        entries = []
        query = ''.join([
            "SELECT entry_num, occurred ",
            " FROM nav.lidar ",
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

            entries.append(Lidar(
                vehicle_id = vehicle_id,
                session_id = session_id,
                entry_num = row[0],
                occurred = row[1]
            ))

        db.close_cursor('q')
        return entries
    
    def get_lidar_data (self, vehicle_id, entry_num):
        lidar_map = None
        lidar_entry = None
        query = ''.join([
            "SELECT session_id, occurred, lidar_data ",
            " FROM nav.lidar ",
            " WHERE vehicle_id =  %s and entry_num = %s "
        ])
        params = (vehicle_id, entry_num)

        db = self.get_db()
        db.get_cursor('q').execute(query,params)
        row = db.get_cursor('q').fetchone()
        if row is not None:
            lidar_entry = Lidar(
                vehicle_id = vehicle_id,
                session_id = row[0],
                entry_num = entry_num,
                occurred = row[1],
                lidar_data=row[2]
            )

        db.close_cursor('q')
        return lidar_entry


    def create(self, validated_data):
        lidar_entry = Lidar()
        lidar_entry.vehicle_id = validated_data.get('vehicle_id')
        lidar_entry.entry_num = validated_data.get('entry_num')
        lidar_entry.session_id = validated_data.get('session_id')
        lidar_entry.lidar_data = validated_data.get('lidar_data')
        lidar_entry.occurred = validated_data.get('occurred')

        self.__add_lidar_entry(lidar_entry=lidar_entry)
        return lidar_entry

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        logging.getLogger(__name__).info(f"Updating log has no effect: {validated_data}")
        return instance
    
    def __add_lidar_entry (self, lidar_entry : Lidar, db = None):
        logging.getLogger(__name__).info(f"Saving lidar to postgres for: {lidar_entry.vehicle_id}")
        
        sql = ''.join([
            "INSERT INTO nav.lidar ",
            " (vehicle_id, session_id, occurred, lidar_data) ",
            " VALUES (%s, %s, %s, %s) ",
        ])
        params = (
            lidar_entry.vehicle_id,
            lidar_entry.session_id,
            lidar_entry.occurred,
            lidar_entry.lidar_data
        )

        db = self.get_db()
        db.get_cursor('u').execute(sql,params)
        db.commit()
        db.close_cursor('u')
