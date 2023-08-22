INSERT INTO nav.maps (
    map_id, 
    map_content
)
VALUES (
    'basement',
    '{
        "landmarks": {
            "n_light": {
                "pattern":"3",
                "type":"light",
                "model":"lights",
                "x":26,
                "y":132,
                "height":43,
                "altitude":40,
                "confidence":0.25
            },
            "e_light": {
                "pattern":"2",
                "type":"light",
                "model":"lights",
                "x":136,
                "y":-28,
                "height":11,
                "altitude":29,
                "confidence":0.25
            },
            "nw_light": {
                "pattern":"4",
                "type":"light",
                "model":"lights",
                "x":-112,
                "y":130,
                "height":42,
                "altitude":21,
                "confidence":0.25
            },                
            "e_ball": {
                "pattern":"na",
                "type":"gazing_ball",
                "model":"basement",
                "x":72,
                "y":1,
                "height":10.5,
                "altitude":5.25,
                "confidence":0.6
            },
            "w_tree": {
                "pattern":"na",
                "type":"cat_tree",
                "model":"basement",
                "x":-93,
                "y":-52,
                "height":24.5,
                "altitude":12.25,
                "confidence":0.6
            },   
            "w_house": {
                "pattern":"na",
                "type":"house",
                "model":"basement",
                "x":-57,
                "y":1,
                "height":7.75,
                "altitude":3.875,
                "confidence":0.6
            }   
        },
        "shape":"rectangle",
        "boundaries" : {
            "xmin":-50,
            "ymin":-150,
            "xmax":100,
            "ymax":0
        }
    }'

) ON CONFLICT (map_id) DO UPDATE set map_content = EXCLUDED.map_content;