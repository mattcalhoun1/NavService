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

INSERT INTO nav.vehicles (
    vehicle_id,
    vehicle_name,
    is_active)
VALUES (
    'MecCar',
    'Mecanum Car',
    true
)
ON CONFLICT (vehicle_id) DO UPDATE 
set 
    vehicle_name = EXCLUDED.vehicle_name, 
    is_active = EXCLUDED.is_active;


--- Adding an entry so it shows up in app
/*insert into nav.position_log (
  vehicle_id,
  session_id, 
  created,
  occurred,
  position_x,
  position_y,
  heading,
  map_id
) VALUES (
  'MecCar',
  'First',
  now(),
  now(),
  0.0,
  0.0,
  0.0,
  'basement'
);
*/