INSERT INTO nav.maps (
    map_id, 
    map_content,
    file_location
)
VALUES (
    'basement',
    '{}',
    '/home/matt/projects/services/NavService/maps/basement.json'

) 
ON CONFLICT (map_id) 
DO UPDATE 
set 
    map_content = EXCLUDED.map_content,
    file_location = EXCLUDED.file_location
;