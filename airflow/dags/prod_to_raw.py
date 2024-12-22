from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable

from airflow.hooks.postgres_hook import PostgresHook

import datetime

default_args = {
    "start_date": days_ago(1)
}

def get_max_last_updated():
    return Variable.get("max_last_updated", default_var="1970-01-01 00:00:00")

def extract_new_records(**context):
    max_last_updated = context['ti'].xcom_pull(task_ids='get_max_last_updated_task')
    
    source_hook = PostgresHook(postgres_conn_id='first_service')
    sql_query = f"""
        SELECT *
        FROM "order"
        WHERE updated_at > '{max_last_updated}'
        ORDER BY updated_at ASC
    """
    rows = source_hook.get_records(sql_query)
    return rows

def load_new_records(**context):
    rows = context['ti'].xcom_pull(task_ids='extract_new_records_task')
    if not rows:
        return
    target_hook = PostgresHook(postgres_conn_id='warehouse_db')

    insert_sql = """
        INSERT INTO raw_orders (
            assigned_order_id, 
            order_id, 
            executer_id, 
            status, 
            coin_coeff, 
            coin_bonus_amount, 
            final_coin_amount, 
            route_information, 
            assign_time, 
            acquire_time, 
            updated_at
        )
        VALUES (
            %s, %s, %s, %s, 
            %s, %s, %s, %s, 
            %s, %s, %s
        )
        ON CONFLICT (assigned_order_id) 
        DO UPDATE SET
            order_id           = EXCLUDED.order_id,
            executer_id        = EXCLUDED.executer_id,
            status             = EXCLUDED.status,
            coin_coeff         = EXCLUDED.coin_coeff,
            coin_bonus_amount  = EXCLUDED.coin_bonus_amount,
            final_coin_amount  = EXCLUDED.final_coin_amount,
            route_information  = EXCLUDED.route_information,
            assign_time        = EXCLUDED.assign_time,
            acquire_time       = EXCLUDED.acquire_time,
            updated_at         = EXCLUDED.updated_at;

    """
    target_hook.run(insert_sql, parameters=rows)
    
    latest_updated = max(row[-1] for row in rows)
    
    Variable.set("max_last_updated", str(latest_updated))

with DAG(
        'incremental_copy',
        schedule_interval='@hourly',
        default_args=default_args,
        catchup=False
    ) as dag:
    get_max_last_updated_task = PythonOperator(
        task_id='get_max_last_updated_task',
        python_callable=get_max_last_updated
    )

    extract_new_records_task = PythonOperator(
        task_id='extract_new_records_task',
        python_callable=extract_new_records,
        provide_context=True
    )

    load_new_records_task = PythonOperator(
        task_id='load_new_records_task',
        python_callable=load_new_records,
        provide_context=True
    )

    get_max_last_updated_task >> extract_new_records_task >> load_new_records_task


if __name__ == "__main__":
    dag.test()
