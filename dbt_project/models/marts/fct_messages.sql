-- This is the main fact table, bringing everything together into a single,
-- queryable model. It represents the core events of our data: messages being sent.

-- Import the staging model for messages
with messages as (
    select * from {{ ref('stg_telegram_messages') }}
),

-- Import the dimension model for channels
channels as (
    select * from {{ ref('dim_channels') }}
)

-- Final SELECT statement to build the fact table
select
    -- Create a unique surrogate key for each message in a channel
    {{ dbt_utils.generate_surrogate_key(['messages.message_id', 'messages.channel_name']) }} as message_key,
    
    -- Foreign keys to link to dimension tables
    channels.channel_key,
    messages.message_date::date as date_key,

    -- Message details
    messages.message_text,
    messages.sender_id,
    
    -- Business Metrics
    length(messages.message_text) as message_length,
    case when messages.photo_path is not null then 1 else 0 end as has_image

from messages
-- Join with the channels dimension to get the channel foreign key
left join channels on messages.channel_name = channels.channel_name