from rest_framework import serializers
from position.models import Lidar,PositionLog, PositionLogEntry, PositionView, NavMap, Vehicle, NavModel, Assignment, LANGUAGE_CHOICES, STYLE_CHOICES
import logging
from helpers.postgres_helper import PostgresHelper
import json
import base64
from position.serializers.serializer_base import SerializerBase

class NavigationMapSerializer(SerializerBase):
    map_id = serializers.CharField(max_length=32)
    content = serializers.JSONField()
    map_desc = serializers.CharField(max_length=128)

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

    def get_maps (self):
        query = ''.join([
            "SELECT map_id, map_desc, file_location ",
            " FROM nav.maps ",
            " WHERE is_active = true"
        ])
        nav_maps = []

        db = self.get_db()
        db.get_cursor('q').execute(query)

        while True:
            row = db.get_cursor('q').fetchone()
            if row is not None:
                # read the specified file
                map_id = row[0]
                map_desc = row[1]
                map_file = row[2]
                nav_map = None
                with open(map_file) as map_in:
                    file_contents = map_in.read()
                    nav_maps.append(
                        NavMap(
                            map_id = map_id, 
                            content=json.loads(file_contents), 
                            map_desc = map_desc))
            else:
                break

        db.close_cursor('q')
        return nav_maps
