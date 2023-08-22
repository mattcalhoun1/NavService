from rest_framework import serializers
from position.models import PositionLog, PositionLogEntry, NavMap, Vehicle, LANGUAGE_CHOICES, STYLE_CHOICES
import logging
from helpers.postgres_helper import PostgresHelper

class SerializerBase(serializers.Serializer):
    def __init__(self, data, many=False):
        serializers.Serializer.__init__(self, data=data, many=many)
        self.__db = None

    def get_db (self):
        if self.__db is None:
            self.__db = PostgresHelper()
        return self.__db
    
    def cleanup (self):
        if self.__db is not None:
            self.__db.cleanup()


class VehicleSerializer(SerializerBase):
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

class PositionLogEntrySerializer(SerializerBase):
    entry_num = serializers.IntegerField(required=False)
    occurred = serializers.DateTimeField()
    vehicle_id = serializers.CharField(required=True, allow_blank=False, max_length=32)
    session_id = serializers.CharField(required=True, allow_blank=False, max_length=64)
    created = serializers.DateTimeField()
    position_x = serializers.FloatField(required=True)
    position_y = serializers.FloatField(required=True)
    navmap_id = serializers.CharField(required=True, allow_blank=False, max_length=32)

    def get_all_matching (self, vehicle_id, session_id, start_time = None, end_time = None):
        entries = []
        query = ''.join([
            "SELECT created, occurred, position_x, position_y, map_id, entry_num, session_id ",
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
                navmap_id = row[4],
                entry_num = row[5],
                session_id = row[6]
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
        plog.navmap_id = validated_data.get('navmap_id')
        plog.session_id = validated_data.get('session_id')

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
            "INSERT INTO nav.position_log (vehicle_id, created, occurred, position_x, position_y, map_id, session_id) ",
            " VALUES (%s, %s, %s, %s, %s, %s, %s) "
        ])
        params = (
            log_entry.vehicle_id,
            log_entry.created,
            log_entry.occurred,
            log_entry.position_x,
            log_entry.position_y,
            log_entry.navmap_id,
            log_entry.session_id
        )

        db = self.get_db()
        db.get_cursor('u').execute(sql,params)
        db.commit()
        db.close_cursor('q')