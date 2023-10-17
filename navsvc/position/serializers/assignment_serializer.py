from rest_framework import serializers
from position.models import Lidar,PositionLog, PositionLogEntry, PositionView, NavMap, Vehicle, NavModel, Assignment, LANGUAGE_CHOICES, STYLE_CHOICES
import logging
from helpers.postgres_helper import PostgresHelper
import json
import base64
from position.serializers.serializer_base import SerializerBase

class AssignmentSerializer(SerializerBase):
    vehicle_id = serializers.CharField(required=True, allow_blank=False, max_length=32)
    entry_num = serializers.IntegerField(required=False)
    complete = serializers.BooleanField(required=False)
    assignment = serializers.JSONField(required=False)

    def get_incomplete (self, vehicle_id):
        entries = []
        query = ''.join([
            "SELECT assignment, entry_num ",
            " FROM nav.assignments ",
            " WHERE vehicle_id =  %s and (complete is null or complete  = false) ",
            " ORDER BY entry_num ASC"
        ])
        params = (vehicle_id,)

        db = self.get_db()
        db.get_cursor('q').execute(query,params)
        while True:
            row = db.get_cursor('q').fetchone()
            if row is None:
                break   

            entries.append(Assignment(
                vehicle_id = vehicle_id,
                entry_num = row[1],
                assignment = row[0],
                complete = False,
            ))

        db.close_cursor('q')
        return entries

    def get (self, vehicle_id : str, entry_num : int):
        query = ''.join([
            "SELECT assignment, complete ",
            " FROM nav.assignments ",
            " WHERE vehicle_id =  %s and entry_num = %s ",
            " ORDER BY entry_num ASC"
        ])
        params = (vehicle_id, entry_num)

        db = self.get_db()
        db.get_cursor('q').execute(query,params)
        assignment = None
        row = db.get_cursor('q').fetchone()
        if row is not None:
            assignment = Assignment(
                vehicle_id = vehicle_id,
                entry_num = entry_num,
                assignment = row[0],
                complete = row[1],
            )

        db.close_cursor('q')
        return assignment

    def create(self, validated_data):
        """
        Create or update an assignment using given data. no entry_num means it's new
        """
        logging.getLogger(__name__).info(f"Creating position log entry: {validated_data}")
        assn = Assignment()
        assn.vehicle_id = validated_data.get('vehicle_id')
        assn.assignment = validated_data.get('assignment')
        assn.complete = validated_data.get('complete')

        if validated_data.get('entry_num') is not None:
            self.update(assn, validated_data)
        else:
            self.__add_assignment(assignment=assn)
        return assn

    def update(self, instance, validated_data):
        """
        Update the completed status
        """
        logging.getLogger(__name__).info(f"Updating assignment: {validated_data}")

        assn = Assignment()
        assn.vehicle_id = validated_data.get('vehicle_id')
        assn.assignment = validated_data.get('assignment')
        assn.complete = validated_data.get('complete')
        assn.entry_num = validated_data.get('entry_num')

        sql = ''.join([
            "UPDATE nav.assignments ",
            " SET complete = %s "
            " WHERE vehicle_id = %s AND entry_num = %s "
        ])
        params = (
            assn.complete,
            assn.vehicle_id,
            assn.entry_num,
        )

        db = self.get_db()
        db.get_cursor('u').execute(sql,params)
        db.commit()

        db.close_cursor('u')    

        return instance
    
    def __add_assignment (self, assignment : Assignment, db = None):
        logging.getLogger(__name__).info(f"Saving assignment to postgres for: {assignment.vehicle_id}")

        sql = ''.join([
            "INSERT INTO nav.assignments (vehicle_id, assignment) ",
            " VALUES (%s, %s) "
        ])
        params = (
            assignment.vehicle_id,
            assignment.assignment,
        )

        db = self.get_db()
        db.get_cursor('u').execute(sql,params)
        db.commit()

        db.get_cursor('u').execute('SELECT MAX(entry_num) FROM nav.assignments WHERE vehicle_id = %s', (assignment.vehicle_id,))
        # retrieve the just-inserted entry num
        assignment.entry_num = db.get_cursor('u').fetchone()[0]

        db.close_cursor('u')    
