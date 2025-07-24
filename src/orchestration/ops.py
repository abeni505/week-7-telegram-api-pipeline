# src/orchestration/ops.py

import subprocess
import os
from dagster import op, OpExecutionContext

# An op is a single unit of computation in a Dagster pipeline.
# Each function decorated with @op represents one step.

@op
def scrape_telegram_data(context: OpExecutionContext):
    """
    Dagster op to run the Telegram scraping process.
    This would typically call your main scraping script.
    """
    context.log.info("Starting Telegram data scraping...")
    
    # In a real project, you would import and call your main scraping function here.
    # For this example, we'll simulate it with a placeholder command.
    # We are assuming you have a main scraping script at 'src/scraping/main.py'
    
    # Example: from src.scraping.main import run_scraper
    # run_scraper()

    # For now, we just log that the step is running.
    # This op can be expanded to call your actual scraping logic.
    context.log.info("Telegram data scraping complete.")
    return True


@op
def run_yolo_enrichment(context: OpExecutionContext, scrape_success: bool):
    """
    Dagster op to run the YOLOv8 image enrichment script.
    This op depends on the scraping op completing successfully.
    """
    if not scrape_success:
        context.log.warning("Skipping YOLO enrichment due to scraping failure.")
        return False
        
    context.log.info("Starting image enrichment with YOLOv8...")
    
    # We use subprocess to run your existing enrichment script.
    # We assume it's executable and located at 'src/enrichment/enrich_images.py'.
    command = ["python", "src/enrichment/enrich_images.py"]
    
    try:
        # We run the script from the root of the project.
        process = subprocess.run(command, check=True, capture_output=True, text=True, cwd=os.getenv("DAGSTER_PROJECT_ROOT", "."))
        context.log.info("YOLO enrichment script output:\n" + process.stdout)
    except subprocess.CalledProcessError as e:
        context.log.error(f"YOLO enrichment failed with error:\n{e.stderr}")
        raise e
        
    context.log.info("Image enrichment complete.")
    return True


@op
def load_raw_to_postgres(context: OpExecutionContext, scrape_success: bool, enrichment_success: bool):
    """
    Dagster op to load all raw data into PostgreSQL.
    This depends on both scraping and enrichment finishing.
    """
    if not (scrape_success and enrichment_success):
        context.log.warning("Skipping data loading due to previous step failure.")
        return False

    context.log.info("Loading raw data to PostgreSQL...")
    
    # Define the loading scripts to be executed
    # We assume you have a loading script for messages.
    loading_scripts = [
        "src/loading/loader.py", # Assumed script for messages
        "src/loading/load_detection_results.py"
    ]
    
    for script_path in loading_scripts:
        context.log.info(f"Running loading script: {script_path}")
        command = ["python", script_path]
        try:
            # We use docker-compose run to ensure the script has network access to the 'db' container.
            # This uses the 'app' service which has all python dependencies installed.
            docker_command = ["docker-compose", "run", "--rm", "app"] + command
            process = subprocess.run(docker_command, check=True, capture_output=True, text=True, cwd=os.getenv("DAGSTER_PROJECT_ROOT", "."))
            context.log.info(f"Output from {script_path}:\n" + process.stdout)
        except subprocess.CalledProcessError as e:
            context.log.error(f"Loading script {script_path} failed with error:\n{e.stderr}")
            raise e
            
    context.log.info("Raw data loading complete.")
    return True


@op
def run_dbt_transformations(context: OpExecutionContext, load_success: bool):
    """
    Dagster op to run dbt transformations.
    This op depends on the data loading successfully.
    """
    if not load_success:
        context.log.warning("Skipping dbt transformations due to loading failure.")
        return False

    context.log.info("Starting dbt transformations...")
    
    # This is the same command you used successfully in the terminal.
    # It runs 'dbt run' inside the dbt service container.
    command = ["docker-compose", "run", "--rm", "dbt", "run"]
    
    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True, cwd=os.getenv("DAGSTER_PROJECT_ROOT", "."))
        context.log.info("dbt run output:\n" + process.stdout)
    except subprocess.CalledProcessError as e:
        context.log.error(f"dbt transformations failed with error:\n{e.stderr}")
        raise e
        
    context.log.info("dbt transformations complete.")
    return True