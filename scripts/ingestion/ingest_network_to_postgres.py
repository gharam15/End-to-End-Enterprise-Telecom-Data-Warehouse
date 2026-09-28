import os
import time
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import requests

from sqlalchemy import create_engine
from dotenv import load_dotenv


# ------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------

load_dotenv()


# ------------------------------------------------------------
# API configuration
# ------------------------------------------------------------

api_key = os.getenv("OPENCELLID_API_KEY")

if not api_key:
    raise ValueError("OPENCELLID_API_KEY is not configured.")


api_url = "https://opencellid.org/cell/getInArea"

bbox = os.getenv(
    "OPENCELLID_BBOX",
    "30.030,31.220,30.045,31.235"
)

mcc = int(os.getenv("OPENCELLID_MCC", "602"))
limit = int(os.getenv("OPENCELLID_LIMIT", "50"))
max_pages = int(os.getenv("OPENCELLID_MAX_PAGES", "20"))


# ------------------------------------------------------------
# PostgreSQL configuration
# ------------------------------------------------------------

postgres_host = os.getenv("POSTGRES_HOST", "localhost")
postgres_port = os.getenv("POSTGRES_PORT", "5433")
postgres_db = os.getenv("POSTGRES_DB", "telecom_dw")
postgres_user = os.getenv("POSTGRES_USER", "postgres")
postgres_password = os.getenv("POSTGRES_PASSWORD", "123")


# ------------------------------------------------------------
# Extract OpenCellID data
# ------------------------------------------------------------

all_cells = []
offset = 0

for page in range(max_pages):

    params = {
        "key": api_key,
        "BBOX": bbox,
        "mcc": mcc,
        "limit": limit,
        "offset": offset,
        "format": "json"
    }

    response = requests.get(
        api_url,
        params=params,
        timeout=30
    )

    print(
        f"Page {page + 1} | "
        f"Status: {response.status_code} | "
        f"Offset: {offset}"
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"OpenCellID API request failed: "
            f"{response.status_code} - {response.text}"
        )

    data = response.json()

    if "error" in data:
        raise RuntimeError(
            f"OpenCellID API error: {data}"
        )

    cells = data.get("cells", [])

    if not cells:
        print("No more records.")
        break

    all_cells.extend(cells)

    print("Rows received:", len(cells))
    print("Total rows:", len(all_cells))

    if len(cells) < limit:
        break

    offset += limit

    time.sleep(0.5)


# ------------------------------------------------------------
# Stop when API returns no records
# ------------------------------------------------------------

if not all_cells:
    print("No network data returned from OpenCellID.")
    raise SystemExit


# ------------------------------------------------------------
# Convert API response to DataFrame
# ------------------------------------------------------------

df = pd.DataFrame(all_cells)

df["ingestion_timestamp"] = datetime.now(timezone.utc)


# ------------------------------------------------------------
# Basic transformation
# ------------------------------------------------------------

if "source_system" in df.columns:
    df = df.drop(columns=["source_system"])


df = df.drop_duplicates()


numeric_columns = [
    "lat",
    "lon",
    "mcc",
    "mnc",
    "lac",
    "cellid",
    "range",
    "samples"
]

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


# ------------------------------------------------------------
# Standardize column names
# ------------------------------------------------------------

df = df.rename(
    columns={
        "averageSignalStrength": "average_signal_strength"
    }
)


print("Rows after cleaning:", len(df))


# ------------------------------------------------------------
# Save raw snapshot
# ------------------------------------------------------------

output_folder = Path(
    os.getenv(
        "NETWORK_RAW_FOLDER",
        "/opt/airflow/data/raw/network/opencellid"
    )
)

output_folder.mkdir(
    parents=True,
    exist_ok=True
)

today = datetime.now().strftime("%Y-%m-%d")

output_file = (
    output_folder /
    f"opencellid_{today}.parquet"
)

df.to_parquet(
    output_file,
    index=False
)

print("Raw network file saved:", output_file)


# ------------------------------------------------------------
# PostgreSQL connection
# ------------------------------------------------------------

postgres_engine = create_engine(
    f"postgresql+psycopg2://"
    f"{postgres_user}:{postgres_password}"
    f"@{postgres_host}:{postgres_port}/{postgres_db}"
)


# ------------------------------------------------------------
# Load into PostgreSQL staging
# ------------------------------------------------------------

df.to_sql(
    name="network_cells",
    con=postgres_engine,
    schema="staging",
    if_exists="append",
    index=False,
    chunksize=5000
)


print(
    f"Network ingestion completed successfully. "
    f"Rows loaded: {len(df)}"
)


postgres_engine.dispose()