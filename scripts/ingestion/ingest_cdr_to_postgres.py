import os
import pandas as pd
import pyodbc

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime, timezone


# Load environment variables
load_dotenv(".env")


# ============================================================
# PostgreSQL connection
# ============================================================

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


# ============================================================
# Get the latest loaded timestamp from PostgreSQL staging
# ============================================================

watermark_query = text("""
    SELECT MAX(source_loaded_at)
    FROM staging.cdr_usage
""")

with postgres_engine.connect() as conn:
    last_loaded_at = conn.execute(watermark_query).scalar()


print("Last loaded timestamp:", last_loaded_at)


# ============================================================
# SQL Server source connection
# ============================================================

sqlserver_host = os.getenv("SQLSERVER_HOST", "127.0.0.1")
sqlserver_port = os.getenv("SQLSERVER_PORT", "1433")
sqlserver_db = os.getenv("SQLSERVER_DB", "telecom_source_db")
sqlserver_user = os.getenv("SQLSERVER_USER", "sa")
sqlserver_password = (
    os.getenv("SQLSERVER_PASSWORD")
    or os.getenv("SQLSERVER_SA_PASSWORD")
)

sqlserver_conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={sqlserver_host},{sqlserver_port};"
    f"DATABASE={sqlserver_db};"
    f"UID={sqlserver_user};"
    f"PWD={sqlserver_password};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)


# ============================================================
# Extract only new CDR records
# ============================================================

if last_loaded_at is None:

    # First load
    query = """
        SELECT *
        FROM dbo.cdr_usage_raw
        WHERE source_loaded_at IS NOT NULL
        ORDER BY source_loaded_at
    """

    cdr_df = pd.read_sql(query, sqlserver_conn)

else:

    # Incremental load
    query = """
        SELECT *
        FROM dbo.cdr_usage_raw
        WHERE source_loaded_at > ?
        ORDER BY source_loaded_at
    """

    cdr_df = pd.read_sql(
        query,
        sqlserver_conn,
        params=[last_loaded_at]
    )


print(f"New rows extracted: {len(cdr_df)}")


# Stop when there is no new data
if cdr_df.empty:
    print("No new CDR data found.")
    sqlserver_conn.close()
    raise SystemExit


# ============================================================
# Transform CDR data
# ============================================================

# Replace missing activity values with zero
activity_columns = [
    "smsin",
    "smsout",
    "callin",
    "callout",
    "internet"
]

cdr_df[activity_columns] = (
    cdr_df[activity_columns]
    .fillna(0)
)


# Standardize PostgreSQL column naming
cdr_df = cdr_df.rename(
    columns={
        "CellID": "cellid"
    }
)


# Add staging ingestion timestamp
cdr_df["ingestion_timestamp"] = datetime.now(timezone.utc)


# ============================================================
# Load only new records into PostgreSQL staging
# ============================================================

cdr_df.to_sql(
    name="cdr_usage",
    con=postgres_engine,
    schema="staging",
    if_exists="append",
    index=False,
    chunksize=10000
)


print(
    f"Incremental load completed successfully. "
    f"Rows loaded: {len(cdr_df)}"
)


sqlserver_conn.close()