INSERT INTO nav.vehicles (
    vehicle_id,
    vehicle_name)
VALUES (
    'car_1',
    'smoked car'
)
ON CONFLICT (vehicle_id) DO NOTHING;