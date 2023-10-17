from rest_framework import serializers
from position.models import Lidar,PositionLog, PositionLogEntry, PositionView, NavMap, Vehicle, NavModel, Assignment, LANGUAGE_CHOICES, STYLE_CHOICES
import logging
from helpers.postgres_helper import PostgresHelper
import json
import base64
from position.serializers.serializer_base import SerializerBase

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
                additional_params['object_mappings'] = self.__read_label_file(additional_params['mapping_file'])

                nav_model = NavModel(
                    model_id = model_id,
                    model_type = model_type,
                    model_format = model_format,
                    encoded_model=encoded_model,
                    additional_params=additional_params)
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