import os
from pathlib import Path

import pandas as pd

from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv


# ------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------

load_dotenv()


# ------------------------------------------------------------
# Read connection settings
# ------------------------------------------------------------

sqlserver_host = os.getenv("SQLSERVER_HOST", "127.0.0.1")
sqlserver_port = os.getenv("SQLSERVER_PORT", "1433")
sqlserver_db = os.getenv("SQLSERVER_DB", "telecom_source_db")
sqlserver_user = os.getenv("SQLSERVER_USER", "sa")

sqlserver_password = (
    os.getenv("SQLSERVER_PASSWORD")
    or os.getenv("SQLSERVER_SA_PASSWORD")
)


# ------------------------------------------------------------
# CDR source folder
# ------------------------------------------------------------

landing_folder = Path(
    os.getenv(
        "CDR_LANDING_FOLDER",
        "/opt/airflow/data/raw/cdr/telecom_italia"
    )
)

print("CDR landing folder:", landing_folder)


# ------------------------------------------------------------
# Validate source folder
# ------------------------------------------------------------

if not landing_folder.exists():
    raise FileNotFoundError(
        f"CDR landing folder does not exist: {landing_folder}"
    )


# ------------------------------------------------------------
# SQL Server connection
# ------------------------------------------------------------

connection_string = quote_plus(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={sqlserver_host},{sqlserver_port};"
    f"DATABASE={sqlserver_db};"
    f"UID={sqlserver_user};"
    f"PWD={sqlserver_password};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

sqlserver_engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={connection_string}",
    fast_executemany=True
)


# ------------------------------------------------------------
# Find all CDR files
# ------------------------------------------------------------

csv_files = sorted(
    landing_folder.glob("sms-call-internet-mi-*.csv")
)

print(f"CDR files found: {len(csv_files)}")


if not csv_files:
    print("No CDR files found.")
    raise SystemExit


# ------------------------------------------------------------
# Process CDR files
# ------------------------------------------------------------

for file in csv_files:

    file_name = file.name

    # --------------------------------------------------------
    # Check whether the file was already loaded
    # --------------------------------------------------------

    check_query = text("""
        SELECT COUNT(*)
        FROM dbo.file_load_log
        WHERE file_name = :file_name
          AND load_status = 'SUCCESS'
    """)

    with sqlserver_engine.connect() as conn:
        already_loaded = conn.execute(
            check_query,
            {"file_name": file_name}
        ).scalar()


    if already_loaded:
        print(f"Already loaded: {file_name}")
        continue


    print(f"Loading: {file_name}")


    try:

        # ----------------------------------------------------
        # Read source file
        # ----------------------------------------------------

        cdr_df = pd.read_csv(file)


        # ----------------------------------------------------
        # Add source metadata
        # ----------------------------------------------------

        cdr_df["source_file"] = file_name
        cdr_df["source_loaded_at"] = (
            pd.Timestamp.utcnow().tz_localize(None)
        )

        rows_loaded = len(cdr_df)


        # ----------------------------------------------------
        # Load into SQL Server source
        # ----------------------------------------------------

        cdr_df.to_sql(
            name="cdr_usage_raw",
            con=sqlserver_engine,
            schema="dbo",
            if_exists="append",
            index=False,
            chunksize=10000
        )


        # ----------------------------------------------------
        # Register successful file load
        # ----------------------------------------------------

        log_query = text("""
            INSERT INTO dbo.file_load_log (
                file_name,
                load_status,
                rows_loaded,
                load_timestamp
            )
            VALUES (
                :file_name,
                'SUCCESS',
                :rows_loaded,
                SYSDATETIME()
            )
        """)

        with sqlserver_engine.begin() as conn:
            conn.execute(
                log_query,
                {
                    "file_name": file_name,
                    "rows_loaded": rows_loaded
                }
            )


        print(
            f"Loaded successfully: {file_name} "
            f"({rows_loaded} rows)"
        )


    except Exception as error:

        print(f"Failed: {file_name}")
        print(error)

        raise


# ------------------------------------------------------------
# Close SQLAlchemy engine
# ------------------------------------------------------------

sqlserver_engine.dispose()

print("CDR file loading process completed.")