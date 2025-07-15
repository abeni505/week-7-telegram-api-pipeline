-- This is the main fact table, bringing everything together.

with messages as (
    select * from {{ ref('stg_telegram_messages') }}
),

channels as (
    select * from {{ ref('dim_channels') }}
)

select
    -- Surrogate key for the fact table
    -- We specify messages.channel_name to resolve the ambiguity
    {{ dbt_utils.generate_surrogate_key(['messages.message_id', 'messages.channel_name']) }} as message_key,
    
    -- Foreign keys
    channels.channel_key,
    messages.message_date::date as date_key,

    -- Message details
    messages.message_text,
    messages.sender_id,
    
    -- Metrics
    length(messages.message_text) as message_length,
    case when messages.photo_path is not null then 1 else 0 end as has_image

from messages
left join channels on messages.channel_name = channels.channel_name