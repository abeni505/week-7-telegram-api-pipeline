-- This model creates a dimension table for Telegram channels.

with channels as (
    select
        distinct channel_name
    from {{ ref('stg_telegram_messages') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['channel_name']) }} as channel_key,
    channel_name
from channels