-- This model cleans and restructures the raw JSON data.

with source as (
    select * from {{ source('raw_telegram', 'raw_messages') }}
),

renamed as (
    select
        channel_name,
        (message_data ->> 'id')::bigint as message_id,
        (message_data ->> 'date')::timestamp as message_date,
        message_data ->> 'text' as message_text,
        (message_data ->> 'sender_id')::bigint as sender_id,
        message_data ->> 'photo_path' as photo_path
    from source
)

select * from renamed