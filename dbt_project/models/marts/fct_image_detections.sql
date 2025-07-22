
-- This model reads the raw JSON data from image detections, unnests it,
-- and creates a structured fact table.

WITH raw_image_detections AS (
    -- This CTE should point to the table where you load your raw JSON detection data.
    -- For this to work, you must first have a process to load the JSON files from
    -- `data/processed/image_detections/` into a raw table, e.g., `raw_data.image_detections`.
    -- We'll assume that table has a single JSONB column named `data`.
    SELECT
        data AS detection_data
    FROM {{ source('raw_data', 'image_detections') }}
),

-- The `jsonb_array_elements` function in PostgreSQL is used to expand a JSON array
-- into a set of rows, which is perfect for our detection results.
unpacked_detections AS (
    SELECT
        jsonb_array_elements(detection_data) AS detection
    FROM
        raw_image_detections
)

-- Final selection and type casting to build our clean fact table.
SELECT
    (detection ->> 'message_id')::INTEGER AS message_id,
    detection ->> 'detected_object_class' AS detected_object_class,
    (detection ->> 'confidence_score')::FLOAT AS confidence_score,
    -- Extract bounding box coordinates from the nested array
    (detection -> 'bounding_box' ->> 0)::FLOAT AS box_x1,
    (detection -> 'bounding_box' ->> 1)::FLOAT AS box_y1,
    (detection -> 'bounding_box' ->> 2)::FLOAT AS box_x2,
    (detection -> 'bounding_box' ->> 3)::FLOAT AS box_y3
FROM
    unpacked_detections
