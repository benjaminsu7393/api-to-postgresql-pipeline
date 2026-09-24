import requests
import pandas as pd
import logging
import os

from sqlalchemy import create_engine
from pathlib import Path
from dotenv import load_dotenv
from requests.exceptions import RequestException
from sqlalchemy.exc import SQLAlchemyError

#print("RUNNING FILE:", __file__)


# --------------------------------------------------
# LOGGING
# --------------------------------------------------

log_dir = Path(__file__).resolve().parent.parent / "logs"

log_dir.mkdir(exist_ok=True)

log_file = log_dir / "pipeline.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logging.info("Pipeline started.")
# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

project_root = Path(__file__).resolve().parent.parent

load_dotenv(project_root / ".env")


# Logging into Postgres 
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

#print("DB_USER:", db_user)
#print("DB_HOST:", db_host)
#print("DB_PORT:", db_port)
#print("DB_NAME:", db_name)



# Connect Python to the practice_db PostgreSQL database
engine = create_engine(
    f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)


# --------------------------------------------------
# EXTRACT
# --------------------------------------------------

# API we want to get product data from
url = "https://dummyjson.com/products"

# Call the API
try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()

except RequestException as error:
    logging.error(f"API request failed: {error}")
    raise SystemExit(1)


# Convert the JSON response into Python data
data = response.json()

# Get the products list from the API response
products = data.get("products", [])

# Make sure products were actually returned
if not products:
    logging.error("API returned no products.")
    raise SystemExit(1)

logging.info("API data successfully extracted.")

# --------------------------------------------------
# TRANSFORM
# --------------------------------------------------

# Turn the product list into a pandas DataFrame
df = pd.DataFrame(products)

required_columns = {
    "id",
    "title",
    "price",
    "category",
    "stock"
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    logging.error(
        f"Missing required columns: {missing_columns}"
    )
    raise SystemExit(1)



# Keep only the columns we want
df = df[
    [
        "id",
        "title",
        "price",
        "category",
        "stock"
    ]
]

# Rename id to something more descriptive
df = df.rename(
    columns={
        "id": "product_id"
    }
)

logging.info(f"{len(df)} products successfully transformed.")

# --------------------------------------------------
# DATA QUALITY CHECKS
# --------------------------------------------------

if df["product_id"].isnull().any():
    logging.error("Null product IDs found.")
    raise SystemExit(1)

if df["product_id"].duplicated().any():
    logging.error("Duplicate product IDs found.")
    raise SystemExit(1)

if df["price"].isnull().any():
    logging.error("Null prices found.")
    raise SystemExit(1)

if (df["price"] < 0).any():
    logging.error("Negative prices found.")
    raise SystemExit(1)

if (df["stock"] < 0).any():
    logging.error("Negative stock values found.")
    raise SystemExit(1)

logging.info("Data quality checks passed.")

try:

    # Replace the staging table with the latest API data
    df.to_sql(
        "products_staging",
        engine,
        if_exists="replace",
        index=False
    )

    logging.info("products_staging successfully loaded.")

    # Find the upsert SQL file
    sql_file = (
        Path(__file__).resolve().parent.parent
        / "sql"
        / "upsert_products.sql"
    )

    # Read the SQL code from the file
    try:
        upsert_sql = sql_file.read_text()
    except OSError as error: 
        logging.error(f"Unable to read SQL file: {error}")
        raise SystemExit(1)

    # Execute the SQL against PostgreSQL
    with engine.begin() as connection:
        connection.exec_driver_sql(upsert_sql)

    logging.info("products table successfully updated.")


except SQLAlchemyError as error:
    logging.error(f"Database operation failed: {error}")
    raise SystemExit(1)



logging.info("Pipeline completed successfully.")

