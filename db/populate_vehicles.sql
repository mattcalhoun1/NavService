INSERT INTO nav.vehicles (
    vehicle_id,
    vehicle_name)
VALUES (
    'car_1',
    'smoked car'
)
ON CONFLICT (vehicle_id) DO NOTHING;

INSERT INTO nav.vehicles (
    vehicle_id,
    vehicle_name)
VALUES (
    'tank_1',
    'Tank Prototype'
)
ON CONFLICT (vehicle_id) DO NOTHING;