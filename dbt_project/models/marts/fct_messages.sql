-- models/marts/fct_messages.sql

WITH messages AS (
    SELECT * FROM {{ ref('stg_telegram_messages') }}
),
channels AS (
    SELECT * FROM {{ ref('dim_channels') }}
),
dates AS (
    SELECT * FROM {{ ref('dim_dates') }}
)

SELECT
    -- --- FIX: Use the correct column from the channels dimension to generate the key ---
    {{ dbt_utils.generate_surrogate_key(['messages.message_id', 'channels.channel_key']) }} AS message_key,

    -- This is the natural key that will be used to join with fct_image_detections
    messages.message_id,

    -- Foreign keys
    channels.channel_key,
    dates.date_key,

    -- Message content and metrics
    messages.message_text
FROM
    messages
-- Join on the channel_name column, which exists in both models
LEFT JOIN channels ON messages.channel_name = channels.channel_name
-- Join on the correct date column and cast the type
LEFT JOIN dates ON messages.message_date::date = dates.date_key

