-- This model creates a comprehensive date dimension table.

select
  date_day::date as date_key,
  extract(year from date_day) as year,
  extract(month from date_day) as month,
  extract(day from date_day) as day,
  extract(dow from date_day) as day_of_week,
  to_char(date_day, 'Day') as day_name,
  to_char(date_day, 'Month') as month_name
from (
    -- This generates a series of dates. Adjust the range as needed.
    select generate_series(
        '2020-01-01'::date,
        '2025-12-31'::date,
        '1 day'::interval
    ) as date_day
) as dates