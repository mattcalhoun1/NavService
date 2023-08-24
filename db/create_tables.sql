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
    map_id VARCHAR(32),
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
    camera_angle float, -- 0 = front of vehicle, +90 directly left, etc
    image_format VARCHAR(4), -- ex: png
    encoded_image bytea, -- the actual jpeg/png/etc bytes
    PRIMARY KEY (vehicle_id, entry_num, camera_id),
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