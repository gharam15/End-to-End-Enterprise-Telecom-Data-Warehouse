import os
import pandas as pd
import pyodbc

from sqlalchemy import create_engine, text
from dotenv import load_dotenv


# ------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------

load_dotenv()


# ------------------------------------------------------------
# Connection settings
# ------------------------------------------------------------

postgres_host = os.getenv("POSTGRES_HOST", "localhost")
postgres_port = os.getenv("POSTGRES_PORT", "5433")
postgres_db = os.getenv("POSTGRES_DB", "telecom_dw")
postgres_user = os.getenv("POSTGRES_USER", "postgres")
postgres_password = os.getenv("POSTGRES_PASSWORD", "123")

sqlserver_host = os.getenv("SQLSERVER_HOST", "127.0.0.1")
sqlserver_port = os.getenv("SQLSERVER_PORT", "1433")
sqlserver_db = os.getenv("SQLSERVER_DB", "telecom_source_db")
sqlserver_user = os.getenv("SQLSERVER_USER", "sa")

sqlserver_password = (
    os.getenv("SQLSERVER_PASSWORD")
    or os.getenv("SQLSERVER_SA_PASSWORD")
)


# ------------------------------------------------------------
# PostgreSQL connection
# ------------------------------------------------------------

postgres_engine = create_engine(
    f"postgresql+psycopg2://"
    f"{postgres_user}:{postgres_password}"
    f"@{postgres_host}:{postgres_port}/{postgres_db}"
)


# ------------------------------------------------------------
# Get current billing watermark
# ------------------------------------------------------------

watermark_query = text("""
    SELECT COALESCE(MAX(billing_id), 0)
    FROM staging.billing
""")

with postgres_engine.connect() as conn:
    last_billing_id = conn.execute(watermark_query).scalar()


print(f"Last billing ID: {last_billing_id}")


# ------------------------------------------------------------
# SQL Server connection
# ------------------------------------------------------------

sqlserver_conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={sqlserver_host},{sqlserver_port};"
    f"DATABASE={sqlserver_db};"
    f"UID={sqlserver_user};"
    f"PWD={sqlserver_password};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)


# ------------------------------------------------------------
# Extract new billing rows only
# ------------------------------------------------------------

query = """
    SELECT *
    FROM dbo.billing_transactions
    WHERE billing_id > ?
    ORDER BY billing_id
"""

billing_df = pd.read_sql(
    query,
    sqlserver_conn,
    params=[last_billing_id]
)


print(f"New billing rows extracted: {len(billing_df)}")


# ------------------------------------------------------------
# Stop when no new rows exist
# ------------------------------------------------------------

if billing_df.empty:

    print("No new billing data found.")

    sqlserver_conn.close()
    postgres_engine.dispose()

    raise SystemExit


# ------------------------------------------------------------
# Load into PostgreSQL staging
# ------------------------------------------------------------

billing_df.to_sql(
    name="billing",
    con=postgres_engine,
    schema="staging",
    if_exists="append",
    index=False,
    chunksize=10000
)


print(
    f"Incremental billing load completed successfully. "
    f"Rows loaded: {len(billing_df)}"
)


# ------------------------------------------------------------
# Close connections
# ------------------------------------------------------------

sqlserver_conn.close()
postgres_engine.dispose()