import logging
from helpers.postgres_helper import PostgresHelper
import json
import base64
import os

# this script exports all position images from a give session
class SessionExporter:
    def __init__(self):
        self.__db = None

    def export_session (self, vehicle_id, session_id, out_dir):
        if not os.path.exists(f"{out_dir}/{session_id}"):
            os.makedirs(f"{out_dir}/{session_id}")

        matches = self.get_all_matching_images(vehicle_id=vehicle_id, session_id=session_id)
        for m in matches:
            self.save_position_image(
                vehicle_id=vehicle_id,
                entry_num = m['entry_num'],
                camera_id=m['camera_id'],
                file_name=f"{out_dir}/{session_id}/{m['entry_num']}_{m['camera_id']}_{m['camera_angle']}.{m['image_format']}")
        self.cleanup()

    def get_all_matching_images (self, vehicle_id, session_id):
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

            entries.append({
                'vehicle_id' : vehicle_id,
                'session_id' : session_id,
                'entry_num' : row[0],
                'camera_id' : row[1],
                'camera_angle' : row[2],
                'image_format' : row[3]
            })

        db.close_cursor('q')
        return entries
    
    def save_position_image (self, vehicle_id, entry_num, camera_id, file_name):
        success = False
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
            with open(file_name, 'wb') as img_out:
                img_out.write(raw_image)
            success = True

        db.close_cursor('q')
        return success

    def get_db (self):
        if self.__db is None:
            self.__db = PostgresHelper()
        return self.__db
    
    def cleanup (self):
        if self.__db is not None:
            self.__db.cleanup()
            self.__db = None

if __name__ == '__main__':
    exporter = SessionExporter()
    exporter.export_session(
        vehicle_id='MecCar',
        session_id = '2023-11-08',
        out_dir='/home/matt/projects/LVPS_Tests'
    )
