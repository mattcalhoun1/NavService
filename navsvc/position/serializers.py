from rest_framework import serializers
from position.models import PositionLog, PositionLogEntry, NavMap, Vehicle, NavModel, LANGUAGE_CHOICES, STYLE_CHOICES
import logging
from helpers.postgres_helper import PostgresHelper
import json
import base64

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

# from https://www.reddit.com/r/django/comments/v2s3fv/django_rest_framework_with_base64_image/
class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

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

class NavigationModelSerializer(SerializerBase):
    model_id = serializers.CharField(max_length=32)
    model_type = serializers.CharField(max_length=32)
    model_format = serializers.CharField(max_length=32)
    additional_params = serializers.JSONField()
    encoded_model = serializers.CharField()

    def get_model (self, model_id, model_type, model_format):
        query = ''.join([
            "SELECT model_type, model_format, additional_params, file_location ",
            " FROM nav.models ",
            " WHERE model_id =  %s and model_type = %s and model_format = %s"
        ])
        params = (model_id, model_type, model_format)
        nav_model = None

        db = self.get_db()
        db.get_cursor('q').execute(query,params)
        row = db.get_cursor('q').fetchone()
        if row is not None:
            # read the specified file
            model_file = row[3]
            additional_params = row[2] # should contain mapping text file
            with open(model_file, 'rb') as model_in:
                file_contents = model_in.read()
                encoded_model = base64.b64encode(file_contents).decode('utf-8')

                nav_model = NavModel(
                    model_id = model_id,
                    model_type = model_type,
                    model_format = model_format,
                    encoded_model=encoded_model,
                    additional_params={'object_mappings':self.__read_label_file(additional_params['mapping_file'])})
        else:
            logging.getLogger(__name__).warning(f"Model {model_id} Type {model_type} Format {model_format} Not found!")

        db.close_cursor('q')
        return nav_model
    
    def __read_label_file(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
        ret = {}
        line_count = 0
        for line in lines:
            pair = line.strip().split(maxsplit=1)
            if len(pair) > 1:
                ret[int(pair[0])] = pair[1].strip()
            else:
                ret[line_count] = pair[0].strip()
            line_count += 1
        return ret


class NavigationMapSerializer(SerializerBase):
    map_id = serializers.CharField(max_length=32)
    content = serializers.JSONField()

    def get_map (self, map_id):
        query = ''.join([
            "SELECT file_location ",
            " FROM nav.maps ",
            " WHERE map_id =  %s "
        ])
        params = (map_id,)
        nav_map = None

        db = self.get_db()
        db.get_cursor('q').execute(query,params)
        row = db.get_cursor('q').fetchone()
        if row is not None:
            # read the specified file
            map_file = row[0]
            with open(map_file) as map_in:
                file_contents = map_in.read()
                nav_map = NavMap(map_id = map_id, content=json.loads(file_contents))

        db.close_cursor('q')
        return nav_map


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
