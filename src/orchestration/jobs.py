# src/orchestration/jobs.py

from dagster import job
from .ops import (
    scrape_telegram_data,
    run_yolo_enrichment,
    load_raw_to_postgres,
    run_dbt_transformations,
)

# A job is the main unit of execution and monitoring in Dagster.
# It is composed of a graph of ops.

@job
def telegram_data_pipeline():
    """
    This job defines the full end-to-end pipeline for processing Telegram data.
    It orchestrates the scraping, enrichment, loading, and transformation steps.
    """
    # The return value of an op is passed as an argument to the next op,
    # which is how Dagster builds the dependency graph.
    
    # 1. Scrape data from Telegram.
    scrape_success = scrape_telegram_data()
    
    # 2. Run YOLO enrichment on the scraped images.
    # This op depends on the successful completion of the scraping op.
    enrichment_success = run_yolo_enrichment(scrape_success)
    
    # 3. Load all raw data into the PostgreSQL database.
    # This op depends on both scraping and enrichment ops.
    load_success = load_raw_to_postgres(scrape_success, enrichment_success)
    
    # 4. Run dbt transformations to build the final data models.
    # This is the final step and depends on the successful loading of data.
    run_dbt_transformations(load_success)

