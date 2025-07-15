-- tests/assert_no_future_dates.sql

-- This test fails if any message in the fact table has a date after today.
-- This is a good sanity check to catch potential data entry or processing errors.

select
    *
from {{ ref('fct_messages') }}
where date_key > current_date