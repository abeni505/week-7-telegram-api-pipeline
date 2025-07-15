-- A message should either have text or a photo. It shouldn't be completely empty.
select
    *
from {{ ref('stg_telegram_messages') }}
where message_text is null and photo_path is null
