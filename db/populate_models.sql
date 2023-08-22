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
    '{"mapping_file":"/home/matt/projects/Robotics/NavigationModels/FinishedModels/basement.txt"}',
    '/home/matt/projects/Robotics/NavigationModels/FinishedModels/basement.tflite'
) 
ON CONFLICT (model_id, model_type, model_format) 
DO NOTHING
;





