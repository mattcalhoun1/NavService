from rest_framework import serializers
from position.models import Lidar,PositionLog, PositionLogEntry, PositionView, NavMap, Vehicle, NavModel, Assignment, LANGUAGE_CHOICES, STYLE_CHOICES
import logging
from helpers.postgres_helper import PostgresHelper
import json
import base64
from position.serializers.serializer_base import SerializerBase

class PositionLogEntrySerializer(SerializerBase):
    entry_num = serializers.IntegerField(required=False)
    occurred = serializers.DateTimeField()
    vehicle_id = serializers.CharField(required=True, allow_blank=False, max_length=32)
    session_id = serializers.CharField(required=True, allow_blank=False, max_length=64)
    created = serializers.DateTimeField()
    position_x = serializers.FloatField(required=True)
    position_y = serializers.FloatField(required=True)
    navmap_id = serializers.CharField(required=True, allow_blank=False, max_length=32)
    heading = serializers.FloatField(required=True)
    basis = serializers.JSONField(required=False)


    def get_recent_sessions (self, vehicle_id, max_sessions = 10):
        entries = []
        query = ''.join([
            " select session_id, max(occurred) as latest from nav.position_log ",
            " where vehicle_id = %s ",
            " group by session_id ",
            " order by latest desc ",
            "limit %s"
        ])
        params = (vehicle_id, max_sessions)

        db = self.get_db()
        db.get_cursor('q').execute(query,params)
        while True:
            row = db.get_cursor('q').fetchone()
            if row is None:
                break   

            entries.append({
                "session_id": row[0],
                "last_activity": row[1]
            })

        db.close_cursor('q')
        return entries

    def get_all_matching (self, vehicle_id, session_id, start_time = None, end_time = None):
        entries = []
        query = ''.join([
            "SELECT created, occurred, position_x, position_y, heading, map_id, entry_num, session_id, basis ",
            " FROM nav.position_log ",
            " WHERE vehicle_id =  %s and session_id = %s "
        ])
        params = (vehicle_id, session_id)

        if start_time is not None:
            query = query + " AND occured >= %s "
            params = (vehicle_id,session_id, start_time)
        if end_time is not None:
            query = query + " AND occurred <= %s "
            params = (vehicle_id,session_id, end_time) if start_time is None else (vehicle_id,session_id, start_time,end_time)
        query = query + " ORDER BY entry_num asc"

        db = self.get_db()
        db.get_cursor('q').execute(query,params)
        while True:
            row = db.get_cursor('q').fetchone()
            if row is None:
                break   

            entries.append(PositionLogEntry(
                vehicle_id = vehicle_id,
                created = row[0],
                occurred = row[1],
                position_x = row[2],
                position_y = row[3],
                heading = row[4],
                navmap_id = row[5],
                entry_num = row[6],
                session_id = row[7],
                basis = row[8]
            ))

        db.close_cursor('q')
        return entries


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
        plog.heading = validated_data.get('heading')
        plog.navmap_id = validated_data.get('navmap_id')
        plog.session_id = validated_data.get('session_id')
        plog.basis = validated_data.get('basis')

        self.__add_log_entry(log_entry=plog)
        return plog

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        logging.getLogger(__name__).info(f"Updating log has no effect: {validated_data}")
        return instance
    
    def __add_log_entry (self, log_entry : PositionLogEntry, db = None):
        logging.getLogger(__name__).info(f"Saving position log to postgres for: {log_entry.vehicle_id}")
        
        sql = ''.join([
            "INSERT INTO nav.position_log (vehicle_id, created, occurred, position_x, position_y, heading, map_id, session_id, basis) ",
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
        ])
        params = (
            log_entry.vehicle_id,
            log_entry.created,
            log_entry.occurred,
            log_entry.position_x,
            log_entry.position_y,
            log_entry.heading,
            log_entry.navmap_id,
            log_entry.session_id,
            log_entry.basis
        )

        db = self.get_db()
        db.get_cursor('u').execute(sql,params)
        db.commit()

        db.get_cursor('u').execute('SELECT MAX(entry_num) FROM nav.position_log WHERE vehicle_id = %s', (log_entry.vehicle_id,))
        # retrieve the just-inserted entry num
        log_entry.entry_num = db.get_cursor('u').fetchone()[0]

        db.close_cursor('u')
