from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="telecom_billing_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["telecom", "billing"],
) as dag:

    ingest_billing = BashOperator(
        task_id="ingest_billing_to_postgres",
        bash_command="""
        python /opt/airflow/scripts/ingestion/ingest_billing_to_postgres.py
        """
    )

    dbt_run_billing = BashOperator(
        task_id="dbt_run_billing",
        bash_command="""
        cd /opt/airflow/dbt/telecom_dbt &&
        dbt run --select fact_billing mart_billing_summary
        """
    )

    dbt_test_billing = BashOperator(
        task_id="dbt_test_billing",
        bash_command="""
        cd /opt/airflow/dbt/telecom_dbt &&
        dbt test --select fact_billing mart_billing_summary
        """
    )

    ingest_billing >> dbt_run_billing >> dbt_test_billing