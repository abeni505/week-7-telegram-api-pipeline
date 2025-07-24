# src/orchestration/schedules.py

from dagster import ScheduleDefinition, Definitions
from .jobs import telegram_data_pipeline

# A schedule tells Dagster when to execute a job.
daily_schedule = ScheduleDefinition(
    job=telegram_data_pipeline,
    cron_schedule="0 0 * * *",  # This is a cron string for "at midnight every day"
    description="A daily schedule to run the full Telegram data pipeline.",
)

# A Definitions object is what Dagster loads to find all your pipelines,
# assets, schedules, and sensors.
defs = Definitions(
    jobs=[telegram_data_pipeline],
    schedules=[daily_schedule],
)
