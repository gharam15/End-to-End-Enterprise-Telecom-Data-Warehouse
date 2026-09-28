from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="telecom_network_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["telecom", "network"],
) as dag:

    ingest_network = BashOperator(
        task_id="ingest_network_to_postgres",
        bash_command="""
        python /opt/airflow/scripts/ingestion/ingest_network_to_postgres.py
        """
    )

    dbt_run_network = BashOperator(
        task_id="dbt_run_network",
        bash_command="""
        cd /opt/airflow/dbt/telecom_dbt &&
        dbt run --select dim_cell
        """
    )

    dbt_test_network = BashOperator(
        task_id="dbt_test_network",
        bash_command="""
        cd /opt/airflow/dbt/telecom_dbt &&
        dbt test --select dim_cell
        """
    )

    ingest_network >> dbt_run_network >> dbt_test_network