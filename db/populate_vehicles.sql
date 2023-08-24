INSERT INTO nav.vehicles (
    vehicle_id,
    vehicle_name,
    is_active)
VALUES (
    'car_1',
    'smoked car',
    false
)
ON CONFLICT (vehicle_id) DO UPDATE 
set 
    vehicle_name = EXCLUDED.vehicle_name, 
    is_active = EXCLUDED.is_active;

INSERT INTO nav.vehicles (
    vehicle_id,
    vehicle_name,
    is_active)
VALUES (
    'tank_1',
    'Tank Prototype',
    false
)
ON CONFLICT (vehicle_id) DO UPDATE 
set 
    vehicle_name = EXCLUDED.vehicle_name, 
    is_active = EXCLUDED.is_active;

INSERT INTO nav.vehicles (
    vehicle_id,
    vehicle_name,
    is_active)
VALUES (
    'Tank',
    'Red Tank',
    true
)
ON CONFLICT (vehicle_id) DO UPDATE 
set 
    vehicle_name = EXCLUDED.vehicle_name, 
    is_active = EXCLUDED.is_active;
