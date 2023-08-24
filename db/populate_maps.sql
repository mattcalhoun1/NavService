INSERT INTO nav.maps (
    map_id, 
    map_desc,
    map_content,
    file_location,
    is_active
)
VALUES (
    'basement',
    'Basement - Pole 0,0 lights and objects',
    '{}',
    '/home/matt/projects/services/NavService/maps/basement.json',
    true

) 
ON CONFLICT (map_id) 
DO UPDATE 
set 
    map_content = EXCLUDED.map_content,
    map_desc = EXCLUDED.map_desc,
    file_location = EXCLUDED.file_location,
    is_active = EXCLUDED.is_active
;