# Shipping a Data Product - From Telegram to Analytical API

This project is an end-to-end data pipeline that extracts data from public Telegram channels, transforms it using dbt, enriches it with object detection using YOLOv8, and exposes the final insights through a FastAPI analytical API.

## Table of Contents
- [Overview](#overview)
- [How It Works](#how-it-works)
- [Task Accomplished](#task-acomplished)
- [Prerequisites](#prerequisites)
- [Project Setup](#project-setup)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)

## Overview

The primary goal is to build a robust data platform to generate insights about Ethiopian medical businesses from public Telegram data. The pipeline follows a modern ELT framework.

- **Extract & Load**: Scrapes data from Telegram channels and loads it into a PostgreSQL data warehouse.
- **Transform**: Uses dbt to clean, test, and model the raw data into a star schema.
- **Enrich**: Uses YOLOv8 to detect objects in images.
- **Serve**: Exposes cleaned data via a FastAPI.

## How It Works

The pipeline is orchestrated by the `src/main.py` script and runs in the following sequence:

1.  **Data Scraping**: The `scraper.py` script connects to the Telegram API and downloads messages and images from the specified channels, saving them to the `data/raw/` directory.
2.  **Data Loading**: The `loader.py` script reads the raw JSON files from the data lake, truncates the target table to prevent duplicates, and loads the data into the `raw.raw_messages` table in PostgreSQL.
3.  **Data Transformation**: The script then executes `dbt run`, which transforms the raw data into a clean, structured star schema.
4.  **Data Testing**: Finally, `dbt test` is executed to run all data quality tests on the final models, ensuring integrity and reliability.

## Task Acomplished

### Task 0: Project Setup & Environment Management
- [x] Initialized a Git repository for the project.
- [x] Set up a `Dockerfile` and `docker-compose.yml` to containerize the application and PostgreSQL database.
- [x] Created a `.env` file for secure management of secrets and added it to `.gitignore`.
- [x] Established a clean and scalable project structure.

### Task 1: Data Scraping and Collection
- [x] Developed a scraper using Telethon to extract messages and images.
- [x] Implemented a separate login script to handle authentication robustly.
- [x] Stored raw data in a partitioned JSON structure in the `data/` directory.
- [x] Added logging to track progress and channel-specific errors.

### Task 2: Data Modeling and Transformation
- [x] Wrote a script to load raw JSON data from the data lake into PostgreSQL.
- [x] Set up a dbt project with a `profiles.yml` for database connection.
- [x] Developed staging models to clean and cast raw data.
- [x] Implemented a star schema with dimension and fact tables (`dim_channels`, `dim_dates`, `fct_messages`).
- [x] Added built-in and custom dbt tests to ensure data quality and integrity.


## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop)
- Python 3.9+

## Project Setup


Follow these steps to set up and run the project locally.

#### Step 1: Clone the Repository
```bash
git clone https://github.com/abeni505/week-7-telegram-api-pipeline.git 
cd week-7-telegram-api-pipeline
```
#### Step 2: Configure Environment Variables


Create a `.env` file in the project root and add the following variables:
```bash
# .env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
POSTGRES_USER=myadmin
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=mydatabase

*Replace the values with your actual credentials.*
```


#### Step 3:  Build and run the Docker containers:

This command builds the application image, installing all dependencies from `requirements.txt`.


```bash
docker-compose up --build
```

#### Step 4: One-Time Telegram Login

You must log in to Telegram once to create a session file.

```bash
docker-compose run --rm app python src/login.py
```
Follow the prompts to enter your phone number and the code you receive from Telegram.

#### Step 5: Install dbt Packages
This command installs the necessary dbt packages, like `dbt_utils`.

```bash
docker-compose run --rm app dbt deps --project-dir ./dbt_project
```


## Running the Application

To start the application, run:
```bash
docker-compose up
```
To stop the application, run:

```bash
docker-compose down
```

## Project Structure

```bash
week-7-telegram-api-pipeline/
├── .env                  # Stores all secrets and environment variables.
├── .gitignore            # Specifies files and folders for Git to ignore.
├── data/                 # Contains the raw data scraped from Telegram.
│   └── raw/
├── dbt_project/          # The main directory for the dbt project.
│   ├── models/           # Contains all dbt models (SQL files).
│   │   ├── staging/      # Models for cleaning and preparing raw data.
│   │   └── marts/        # Models for the final star schema (facts and dimensions).
│   ├── tests/            # Contains custom dbt data tests.
│   ├── dbt_project.yml   # Main configuration file for the dbt project.
│   └── packages.yml      # Defines dbt packages to be installed.
├── src/                  # Contains all Python source code for the application.
│   ├── __init__.py
│   ├── main.py           # The main entry point for the application pipeline.
│   ├── scraping/         # Code for scraping Telegram data.
│   └── loading/          # Code for loading data into the database.
├── Dockerfile            # Instructions for building the Python application's Docker image.
├── docker-compose.yml    # Defines and configures the multi-service application (app, db).
├── profiles.yml          # dbt connection settings (ignored by Git).
├── requirements.txt      # Lists all Python dependencies for the project.
└── README.md             # This file. Project overview and instructions.
```

## Author

Abenezer M. woldesenbet
