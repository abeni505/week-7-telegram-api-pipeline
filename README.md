# Shipping a Data Product - From Telegram to Analytical API

This project is an end-to-end data pipeline that extracts data from public Telegram channels, transforms it using dbt, enriches it with object detection using YOLOv8, serves insights via a FastAPI, and is fully orchestrated by Dagster.

---

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Tasks Accomplished](#tasks-accomplished)
- [Prerequisites](#prerequisites)
- [Project Setup](#project-setup)
- [Running the Application](#running-the-application)
  - [Running the API Server](#running-the-api-server)
  - [Running the Dagster Pipeline](#running-the-dagster-pipeline)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Author](#author)

---

## Overview

The primary goal is to build a robust data platform to generate insights about Ethiopian medical businesses from public Telegram data. The pipeline follows a modern ELT framework and is designed to be reproducible, scalable, and observable.

- **Extract:** Scrapes messages and images from Telegram channels.
- **Enrich:** Uses a pre-trained YOLOv8 model to detect objects in the scraped images.
- **Load:** Loads the raw messages and enrichment results into a PostgreSQL data warehouse.
- **Transform:** Uses dbt to clean, test, and model the raw data into an analytical star schema.
- **Serve:** Exposes the cleaned data and insights through a FastAPI application.
- **Orchestrate:** Uses Dagster to define, monitor, and schedule the entire end-to-end pipeline.

---

## How It Works

The entire pipeline is defined and managed as a **Dagster job**. This provides a robust, observable, and schedulable workflow.

1. **Telegram Scraping:** A Dagster op downloads new messages and images, saving them to `data/raw/`.
2. **Image Enrichment:** Runs YOLOv8 on the images, generating JSON files in `data/processed/`.
3. **Data Loading:** Loads raw JSON files into the PostgreSQL database.
4. **DBT Transformation:** Executes `dbt run` and `dbt test` to build a clean star schema with data quality tests.

Each step is a node in the Dagster job graph, ensuring correct order and graceful failure handling.

---

## Tasks Accomplished

### Task 0: Project Setup & Environment Management

- [x] Initialized Git repository.
- [x] Set up `Dockerfile` and `docker-compose.yml`.
- [x] Created `.env` for secrets.
- [x] Established scalable project structure.

### Task 1: Data Scraping and Collection

- [x] Scraper for Telegram messages and images.
- [x] Partitioned raw data storage.

### Task 2: Data Modeling and Transformation

- [x] Scripts to load JSON data into PostgreSQL.
- [x] dbt project with staging and mart models.
- [x] Data quality tests.

### Task 3: Data Enrichment with Object Detection

- [x] YOLOv8 enrichment script.
- [x] Fact table `fct_image_detections` for results.
- [x] Linked detection results to core models.

### Task 4: Build an Analytical API

- [x] FastAPI app with modular structure.
- [x] Analytical endpoints.
- [x] Data validation with Pydantic.

### Task 5: Pipeline Orchestration

- [x] Installed and configured Dagster.
- [x] Converted steps into Dagster ops.
- [x] Assembled a Dagster job with scheduling and monitoring.

---

## Prerequisites

- Docker
- Python 3.9+

---

## Project Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/abeni505/week-7-telegram-api-pipeline.git
cd week-7-telegram-api-pipeline
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root by copying the example and add your credentials:

```env
# .env

# Telegram API Credentials
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# PostgreSQL Credentials
POSTGRE_USER=myadmin
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=mydatabase
```

### Step 3: One-Time Telegram Login

You must log in to Telegram once to create a session file that allows the scraper to run automatically.

```bash
# First, ensure the database is running
docker-compose up -d db

# Run the login script
docker-compose run --rm app python src/scraping/login.py
```

Follow the prompts in your terminal to enter your phone number and the code you receive from Telegram.

## Running the Application

The application is split into two main parts: the Analytical API and the Dagster Orchestrator. You can run them independently.

---

### Running the API Server

This will start the FastAPI server, which you can use to query the data in your warehouse.

```bash
# Start the API and the database
docker-compose up -d app

# To view logs
docker-compose logs -f app
```

The API will be available at http://127.0.0.1:8000, with interactive documentation at http://127.0.0.1:8000/docs.


## Running the Dagster Pipeline

This will launch the Dagster UI, where you can monitor, schedule, and manually execute your data pipeline.

```bash
# Make sure all containers are running
docker-compose up -d

# Launch the Dagster UI
dagster dev -m src.orchestration.schedules
```
The Dagster UI will be available at http://127.0.0.1:3000.


## API Endpoints

### GET /api/search/messages

Searches for messages containing a specific keyword.

- **Query Parameter:** `query` (string)
- **Example:** `http://127.0.0.1:8000/api/search/messages?query=paracetamol`
- **Success Response:** `200 OK` with a JSON array of message objects.

---

### GET /api/channels/{channel_name}/activity

Returns the total number of messages posted in a specific channel.

- **Path Parameter:** `channel_name` (string)
- **Example:** `http://127.0.0.1:8000/api/channels/tikvahpharma/activity`
- **Success Response:** `200 OK` with a JSON object containing the message count.
- **Failure Response:** `404 Not Found` if the channel does not exist.

---

### GET /api/reports/top-products

Returns the most frequently mentioned medical products across all channels.

- **Query Parameter:** `limit` (integer, default: 10)
- **Example:** `http://127.0.0.1:8000/api/reports/top-products?limit=5`
- **Success Response:** `200 OK` with a JSON array of product objects and their mention counts.

---

## Project Structure

```bash
week-7-telegram-api-pipeline/
├── .env
├── .gitignore
├── data/
│   ├── processed/
│   │   └── image_detections/
│   └── raw/
│       ├── telegram_images/
│       └── telegram_messages/
├── dbt_project/
│   ├── models/
│   │   ├── marts/
│   │   └── staging/
│   ├── dbt_project.yml
│   └── packages.yml
├── src/
│   ├── api/
│   │   ├── crud.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── enrichment/
│   │   └── enrich_images.py
│   ├── loading/
│   │   ├── load_detection_results.py
│   │   └── load_raw_data.py
│   ├── orchestration/
│   │   ├── jobs.py
│   │   ├── ops.py
│   │   └── schedules.py
│   └── scraping/
│       └── scraper.py
├── Dockerfile
├── docker-compose.yml
├── dagster.yaml
├── profiles.yml
├── requirements.txt
└── README.md
```

---

## Author

**Abenezer M. Woldesenbet**
