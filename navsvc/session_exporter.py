import logging
from helpers.postgres_helper import PostgresHelper
import json
import base64
import os
import sys
from datetime import datetime
from tqdm import tqdm
import logging

# this script exports all position images from a give session
class SessionExporter:
    def __init__(self):
        self.__db = None

    def export_session (self, vehicle_id, session_id, out_dir):
        full_output_dir = f"{out_dir}/{vehicle_id}_{session_id}"
        if not os.path.exists(full_output_dir):
            os.makedirs(full_output_dir)

        coords = self.get_all_coordinates(vehicle_id=vehicle_id, session_id=session_id)
        with open(f"{full_output_dir}/coordinates.json", 'w') as json_out:
            json_out.write(json.dumps(coords, indent=2))

        matches = self.get_all_matching_images(vehicle_id=vehicle_id, session_id=session_id)
        for m in tqdm(matches, 'Writing Images'):
            self.save_position_image(
                vehicle_id=vehicle_id,
                entry_num = m['entry_num'],
                camera_id=m['camera_id'],
                file_name=f"{out_dir}/{vehicle_id}_{session_id}/{m['entry_num']}_{m['camera_id']}_{m['camera_angle']}.{m['image_format']}")
        self.cleanup()

    def get_all_coordinates (self, vehicle_id, session_id):
        logging.getLogger(__name__).info(f'Getting logged positions from vehicle: {vehicle_id}, session: {session_id}')
        coordinates = []
        query = ''.join([
            "SELECT created, occurred, position_x, position_y, heading, map_id, entry_num, session_id, basis ",
            " FROM nav.position_log ",
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

            coordinates.append({
                'vehicle_id':vehicle_id,
                'session_id':session_id,
                'created':datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S'),
                'occurred':datetime.strftime(row[1], '%Y-%m-%d %H:%M:%S'),
                'position_x':row[2],
                'position_y':row[3],
                'heading':row[4],
                'navmap_id':row[5],
                'entry_num':row[6],
                'session_id':row[7],
                'basis':row[8]
            })
        logging.getLogger(__name__).info(f'Found {len(coordinates)} logged positions')

        db.close_cursor('q')
        return coordinates


    def get_all_matching_images (self, vehicle_id, session_id):
        logging.getLogger(__name__).info(f'Getting positioning images for vehicle: {vehicle_id}, session: {session_id}')
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
        logging.getLogger(__name__).info(f'Found {len(entries)} positioning images')

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
    if len(sys.argv) != 3:
        raise ValueError('Please provide vehicle id and session id (two params, unnamed).')
    
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(module)s:%(message)s', level=logging.DEBUG)
    vid = sys.argv[1]
    session = sys.argv[2]
 
    exporter = SessionExporter()
    exporter.export_session(
        vehicle_id=vid,
        session_id=session,
        out_dir='/home/matt/projects/LVPS_Tests'
    )
