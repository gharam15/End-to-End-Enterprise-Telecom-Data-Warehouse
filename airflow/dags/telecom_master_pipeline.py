from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="telecom_master_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
    default_args=default_args,
    tags=["telecom", "master"],
) as dag:

    trigger_billing = TriggerDagRunOperator(
        task_id="trigger_billing_pipeline",
        trigger_dag_id="telecom_billing_pipeline",
        wait_for_completion=True,
        poke_interval=10,
    )

    trigger_cdr = TriggerDagRunOperator(
        task_id="trigger_cdr_pipeline",
        trigger_dag_id="telecom_cdr_pipeline",
        wait_for_completion=True,
        poke_interval=10,
    )

    trigger_support = TriggerDagRunOperator(
        task_id="trigger_support_pipeline",
        trigger_dag_id="telecom_support_pipeline",
        wait_for_completion=True,
        poke_interval=10,
    )

    trigger_network = TriggerDagRunOperator(
        task_id="trigger_network_pipeline",
        trigger_dag_id="telecom_network_pipeline",
        wait_for_completion=True,
        poke_interval=10,
    )

    source_freshness = BashOperator(
        task_id="source_freshness",
        bash_command="""
        cd /opt/airflow/dbt/telecom_dbt &&
        dbt source freshness
        """
    )

    final_dbt_test = BashOperator(
        task_id="final_dbt_test",
        bash_command="""
        cd /opt/airflow/dbt/telecom_dbt &&
        dbt test
        """
    )

    [
        trigger_billing,
        trigger_cdr,
        trigger_support,
        trigger_network,
    ] >> source_freshness >> final_dbt_test