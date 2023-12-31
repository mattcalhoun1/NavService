INSERT INTO nav.models (
    model_id, 
    model_type, -- ex : object_detection
    model_format, -- ex: tflite
    additional_params, -- ex: obj number / name mapping, etc
    file_location
)
VALUES (
    'basement',
    'object_detection',
    'tflite',
    '{"mapping_file":"/home/matt/projects/services/NavService/models/basement.txt","object_type":"basic","resolution_w":640,"resolution_h":640}',
    '/home/matt/projects/services/NavService/models/basement.tflite'
) 
ON CONFLICT (model_id, model_type, model_format) 
DO UPDATE set
    additional_params = EXCLUDED.additional_params,
    file_location = EXCLUDED.file_location
;

INSERT INTO nav.models (
    model_id, 
    model_type, -- ex : object_detection
    model_format, -- ex: tflite
    additional_params, -- ex: obj number / name mapping, etc
    file_location
)
VALUES (
    'lights',
    'object_detection',
    'tflite',
    '{"mapping_file":"/home/matt/projects/services/NavService/models/lights.txt","object_type":"emitter","resolution_w":640,"resolution_h":640}',
    '/home/matt/projects/services/NavService/models/lights_640.tflite'
) 
ON CONFLICT (model_id, model_type, model_format) 
DO UPDATE set
    additional_params = EXCLUDED.additional_params,
    file_location = EXCLUDED.file_location
;




