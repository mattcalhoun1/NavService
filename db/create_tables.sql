-- Create history table
-- create images table
-- create 'script' table


CREATE SCHEMA IF NOT EXISTS nav;

CREATE TABLE IF NOT EXISTS nav.vehicles (
    vehicle_id VARCHAR(32),
    vehicle_name VARCHAR(64),
    is_active boolean,
    PRIMARY KEY (vehicle_id)
);
CREATE INDEX IF NOT EXISTS idx_veh_act ON nav.vehicles (
    is_active
);


CREATE TABLE IF NOT EXISTS nav.maps (
    map_id VARCHAR(32),
    map_content jsonb,
    file_location VARCHAR(128),
    PRIMARY KEY (map_id)
);

CREATE TABLE IF NOT EXISTS nav.models (
    model_id VARCHAR(32),
    model_type VARCHAR(32), -- ex : object_detection
    model_format VARCHAR(32), -- ex: tflite
    additional_params jsonb, -- ex: obj number / name mapping, etc
    encoded_model bytea, -- the actual tflite model binary
    file_location VARCHAR(128),
    PRIMARY KEY (model_type, model_id, model_format)
);

CREATE TABLE IF NOT EXISTS nav.position_log (
    vehicle_id VARCHAR(32),
    entry_num serial,
    session_id VARCHAR(64),
    created timestamp,
    occurred timestamp,
    position_x float,
    position_y float,
    heading float,
    map_id VARCHAR(32),
    basis jsonb, -- data that went into the calculations
    PRIMARY KEY (vehicle_id, entry_num),
    FOREIGN KEY (vehicle_id) REFERENCES nav.vehicles (vehicle_id),
    FOREIGN KEY (map_id) REFERENCES nav.maps (map_id)
);
CREATE INDEX IF NOT EXISTS idx_pos_log_veh ON nav.position_log (
    vehicle_id
);
CREATE INDEX IF NOT EXISTS idx_pos_log_veh_sess ON nav.position_log (
    vehicle_id,
    session_id
);

CREATE TABLE IF NOT EXISTS nav.position_views (
    vehicle_id VARCHAR(32),
    entry_num int, 
    camera_id VARCHAR(32), -- ex: left, etc
    session_id VARCHAR(64),
    camera_angle float default 0, -- 0 = front of vehicle, +90 directly left, etc
    image_format VARCHAR(4), -- ex: png
    encoded_image bytea, -- the actual jpeg/png/etc bytes
    PRIMARY KEY (vehicle_id, entry_num, camera_id, camera_angle),
    FOREIGN KEY (vehicle_id, entry_num) REFERENCES nav.position_log (vehicle_id, entry_num)
);

CREATE INDEX IF NOT EXISTS idx_pos_view_veh_sess ON nav.position_views (
    vehicle_id,
    session_id
);
CREATE INDEX IF NOT EXISTS idx_pos_view_veh_entry ON nav.position_views (
    vehicle_id,
    entry_num
);
CREATE INDEX IF NOT EXISTS idx_pos_view_veh_entry_angles ON nav.position_views (
    vehicle_id,
    entry_num,
    camera_id
);

CREATE TABLE IF NOT EXISTS nav.assignments (
    vehicle_id VARCHAR(32),
    entry_num serial,
    assignment jsonb,
    complete boolean,
    PRIMARY KEY (vehicle_id, entry_num),
    FOREIGN KEY (vehicle_id) REFERENCES nav.vehicles (vehicle_id)
);

CREATE INDEX IF NOT EXISTS idx_assign_v_c ON nav.assignments (
    vehicle_id,
    complete
);

CREATE TABLE IF NOT EXISTS nav.lidar (
    vehicle_id VARCHAR(32),
    entry_num serial,
    session_id VARCHAR(64),
    occurred timestamp,
    lidar_data jsonb,
    PRIMARY KEY (vehicle_id, entry_num),
    FOREIGN KEY (vehicle_id) REFERENCES nav.vehicles (vehicle_id)
);

CREATE INDEX IF NOT EXISTS idx_lidar_v ON nav.lidar (
    vehicle_id
);

CREATE INDEX IF NOT EXISTS idx_lidar_veh_sess ON nav.lidar (
    vehicle_id,
    session_id
);

CREATE TABLE IF NOT EXISTS nav.search_hits (
    object_type VARCHAR(32), -- type identifier (ex: gazing_ball)
    map_id VARCHAR(32), -- map on which the search occurred
    entry_num serial, 
    occurred timestamp DEFAULT now(),
    est_visual_distance float, -- visual estimated distance (in)
    est_lidar_dist float, -- if lidar measuremnt taken, mm distance from lidar
    vehicle_relative_heading float, -- where the object appears relative to the vehicle
    est_x float, -- estimated map x position of the object
    est_y float, -- estimated map y position of the object
    vehicle_x float, -- vehicle x position at the time of sighting
    vehicle_y float, -- vehicle x position at the time of sighting
    vehicle_heading float, -- vehicle heading at the time of sighting
    confidence float, -- confidence 0 - 1.0 of the match
    vehicle_id VARCHAR(32), -- vehicle that took the measurment
    camera_id VARCHAR(32), -- ex: left, etc
    session_id VARCHAR(64), -- session in which the sighting occurred
    camera_angle float, -- 0 = front of vehicle, +90 directly left, etc
    image_format VARCHAR(4), -- ex: png
    encoded_image bytea, -- the actual jpeg/png/etc bytes
    PRIMARY KEY (object_type, map_id, entry_num),
    FOREIGN KEY (map_id) REFERENCES nav.maps (map_id),    
    FOREIGN KEY (vehicle_id) REFERENCES nav.vehicles (vehicle_id)
);

CREATE INDEX IF NOT EXISTS idx_search_hits_veh_sess ON nav.search_hits (
    vehicle_id,
    session_id
);

CREATE INDEX IF NOT EXISTS idx_search_hits_obj_map ON nav.search_hits (
    object_type,
    map_id
);