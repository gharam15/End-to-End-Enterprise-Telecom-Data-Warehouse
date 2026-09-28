import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timezone
import os
from pathlib import Path

# ------------------------------------------------------------
# Support source file
# ------------------------------------------------------------

support_file = Path(
    os.getenv(
        "SUPPORT_FILE",
        "/opt/airflow/data/raw/support/customer_support_tickets.csv"
    )
)

# ------------------------------------------------------------
# Read support data
# ------------------------------------------------------------

support_df = pd.read_csv(support_file)

print(f"Source rows: {len(support_df)}")


# ------------------------------------------------------------
# Standardize column names
# ------------------------------------------------------------

support_df.columns = (
    support_df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)


# ------------------------------------------------------------
# Handle business-valid missing values
# ------------------------------------------------------------

support_df["resolution"] = (
    support_df["resolution"]
    .fillna("Not Resolved")
)


# ------------------------------------------------------------
# Convert date and time columns
# ------------------------------------------------------------

support_df["date_of_purchase"] = pd.to_datetime(
    support_df["date_of_purchase"],
    errors="coerce"
)

support_df["first_response_time"] = pd.to_datetime(
    support_df["first_response_time"],
    errors="coerce"
)

support_df["time_to_resolution"] = pd.to_datetime(
    support_df["time_to_resolution"],
    errors="coerce"
)


# ------------------------------------------------------------
# Add staging ingestion timestamp
# ------------------------------------------------------------

support_df["ingestion_timestamp"] = datetime.now(timezone.utc)


# ------------------------------------------------------------
# PostgreSQL connection
# ------------------------------------------------------------

postgres_host = os.getenv("POSTGRES_HOST", "localhost")
postgres_port = os.getenv("POSTGRES_PORT", "5433")
postgres_db = os.getenv("POSTGRES_DB", "telecom_dw")
postgres_user = os.getenv("POSTGRES_USER", "postgres")
postgres_password = os.getenv("POSTGRES_PASSWORD", "123")

postgres_engine = create_engine(
    f"postgresql+psycopg2://"
    f"{postgres_user}:{postgres_password}"
    f"@{postgres_host}:{postgres_port}/{postgres_db}"
)


# ------------------------------------------------------------
# Get existing ticket IDs from staging
# ------------------------------------------------------------

existing_query = """
SELECT ticket_id
FROM staging.customer_support
"""

existing_df = pd.read_sql(
    existing_query,
    postgres_engine
)


# ------------------------------------------------------------
# Keep only new support tickets
# ------------------------------------------------------------

if not existing_df.empty:

    support_df = support_df[
        ~support_df["ticket_id"].isin(
            existing_df["ticket_id"]
        )
    ]


print(f"New support rows: {len(support_df)}")


# ------------------------------------------------------------
# Stop when no new data exists
# ------------------------------------------------------------

if support_df.empty:

    print("No new support tickets found.")

else:

    # --------------------------------------------------------
    # Load new tickets into PostgreSQL staging
    # --------------------------------------------------------

    support_df.to_sql(
        name="customer_support",
        con=postgres_engine,
        schema="staging",
        if_exists="append",
        index=False,
        chunksize=5000
    )

    print(
        f"Support load completed successfully. "
        f"Rows loaded: {len(support_df)}"
    )