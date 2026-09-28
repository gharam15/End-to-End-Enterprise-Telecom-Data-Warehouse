from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="telecom_support_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["telecom", "support"],
) as dag:

    ingest_support = BashOperator(
        task_id="ingest_support_to_postgres",
        bash_command="""
        python /opt/airflow/scripts/ingestion/ingest_support_to_postgres.py
        """
    )

    dbt_run_support = BashOperator(
        task_id="dbt_run_support",
        bash_command="""
        cd /opt/airflow/dbt/telecom_dbt &&
        dbt run --select fact_customer_support mart_support_performance
        """
    )

    dbt_test_support = BashOperator(
        task_id="dbt_test_support",
        bash_command="""
        cd /opt/airflow/dbt/telecom_dbt &&
        dbt test --select fact_customer_support mart_support_performance
        """
    )

    ingest_support >> dbt_run_support >> dbt_test_support