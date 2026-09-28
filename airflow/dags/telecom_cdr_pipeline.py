import os
from pathlib import Path
from datetime import datetime, timedelta

import pyodbc

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator


default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


# ------------------------------------------------------------
# Check for new CDR files
# ------------------------------------------------------------

def check_new_cdr_file():

    cdr_folder = Path(
        "/opt/airflow/data/raw/cdr/telecom_italia"
    )

    files = sorted(
        cdr_folder.glob("sms-call-internet-mi-*.csv")
    )

    if not files:
        print("No CDR files found.")
        return "no_new_cdr_file"

    sqlserver_host = os.getenv(
        "SQLSERVER_HOST",
        "sqlserver"
    )

    sqlserver_port = os.getenv(
        "SQLSERVER_PORT",
        "1433"
    )

    sqlserver_db = os.getenv(
        "SQLSERVER_DB",
        "telecom_source_db"
    )

    sqlserver_user = os.getenv(
        "SQLSERVER_USER",
        "sa"
    )

    sqlserver_password = (
        os.getenv("SQLSERVER_PASSWORD")
        or os.getenv("SQLSERVER_SA_PASSWORD")
    )

    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={sqlserver_host},{sqlserver_port};"
        f"DATABASE={sqlserver_db};"
        f"UID={sqlserver_user};"
        f"PWD={sqlserver_password};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

    cursor = conn.cursor()

    try:

        for file in files:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM dbo.file_load_log
                WHERE file_name = ?
                  AND load_status = 'SUCCESS'
                """,
                file.name,
            )

            already_loaded = cursor.fetchone()[0]

            if already_loaded == 0:

                print(
                    f"New CDR file detected: {file.name}"
                )

                return "load_cdr_to_sqlserver"

        print(
            "No new CDR files detected. "
            "Skipping CDR ingestion."
        )

        return "no_new_cdr_file"

    finally:
        cursor.close()
        conn.close()


# ------------------------------------------------------------
# DAG
# ------------------------------------------------------------

with DAG(
    dag_id="telecom_cdr_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["telecom", "cdr"],
) as dag:


    check_cdr_file = BranchPythonOperator(
        task_id="check_new_cdr_file",
        python_callable=check_new_cdr_file,
    )


    no_new_cdr_file = EmptyOperator(
        task_id="no_new_cdr_file",
    )


    load_cdr_to_sqlserver = BashOperator(
        task_id="load_cdr_to_sqlserver",
        bash_command="""
        python /opt/airflow/scripts/ingestion/load_cdr_to_sqlserver.py
        """
    )


    ingest_cdr_to_postgres = BashOperator(
        task_id="ingest_cdr_to_postgres",
        bash_command="""
        python /opt/airflow/scripts/ingestion/ingest_cdr_to_postgres.py
        """
    )


    dbt_run_cdr = BashOperator(
        task_id="dbt_run_cdr",
        bash_command="""
        cd /opt/airflow/dbt/telecom_dbt &&
        dbt run --select dim_cdr_cell fact_cdr_usage mart_network_usage
        """
    )


    dbt_test_cdr = BashOperator(
        task_id="dbt_test_cdr",
        bash_command="""
        cd /opt/airflow/dbt/telecom_dbt &&
        dbt test --select dim_cdr_cell fact_cdr_usage mart_network_usage
        """
    )


    check_cdr_file >> no_new_cdr_file

    (
        check_cdr_file
        >> load_cdr_to_sqlserver
        >> ingest_cdr_to_postgres
        >> dbt_run_cdr
        >> dbt_test_cdr
    )