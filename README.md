# API to PostgreSQL ETL Pipeline

A Python ETL pipeline that extracts product data from a REST API, transforms the data using pandas, and loads it into PostgreSQL using a staging-table and upsert process.

## Project Overview

This project demonstrates a basic end-to-end data engineering workflow.

The pipeline:

1. Extracts product data from the DummyJSON API.
2. Converts the JSON response into a pandas DataFrame.
3. Selects and standardizes the required columns.
4. Loads the latest data into a PostgreSQL staging table.
5. Uses SQL to upsert the staging data into a permanent products table.
6. Logs pipeline activity and errors.
7. Uses environment variables to keep database credentials out of the source code.

## Pipeline Architecture

```text
REST API
   |
   v
Python Requests
   |
   v
JSON Response
   |
   v
Pandas DataFrame
   |
   v
Transform Data
   |
   v
PostgreSQL products_staging
   |
   v
SQL UPSERT
   |
   v
PostgreSQL products
