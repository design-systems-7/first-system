from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow.hooks.postgres_hook import PostgresHook
from datetime import datetime, timedelta

default_args = {
    "start_date": days_ago(1)
}


def get_last_processed_time():
    return Variable.get("marts_last_processed", default_var="1970-01-01 00:00:00")


def update_executor_statistics(**context):
    source_hook = PostgresHook(postgres_conn_id='raw_dwh_layer')
    target_hook = PostgresHook(postgres_conn_id='postgres_marts')

    sql_query = f"""
        WITH OrderStats AS (
            SELECT 
                executer_id,
                AVG(
                    CASE 
                        WHEN acquire_time IS NOT NULL 
                        THEN EXTRACT(EPOCH FROM (acquire_time - assign_time))
                        ELSE NULL 
                    END
                ) as avg_acceptance_seconds,
                COUNT(*) as accepted_orders_count
            FROM "order"
            GROUP BY executer_id
        )
        SELECT 
            executer_id,
            avg_acceptance_seconds as acceptance_time,
            accepted_orders_count
        FROM OrderStats
    """

    executor_stats = source_hook.get_records(sql_query)
    for executor_stat in executor_stats:
        if executor_stat:
            insert_sql = """
                INSERT INTO ExecutorStatistics (
                    executor_id, 
                    acceptance_time, 
                    accepted_orders_count
                )
                VALUES (%s, %s, %s)
                ON CONFLICT (executor_id) 
                DO UPDATE SET
                    acceptance_time = EXCLUDED.acceptance_time,
                    accepted_orders_count = EXCLUDED.accepted_orders_count;
            """
            target_hook.run(insert_sql, parameters=executor_stat)


def update_order_snapshots(**context):
    source_hook = PostgresHook(postgres_conn_id='raw_dwh_layer')
    target_hook = PostgresHook(postgres_conn_id='postgres_marts')

    last_processed = context['ti'].xcom_pull(task_ids='get_last_processed_time_task')
    current_time = datetime.now()

    snapshot_sql = f"""
        WITH current_snapshot AS (
            SELECT 
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_count,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_count,
                COUNT(CASE WHEN status = 'done' THEN 1 END) as done_count,
                AVG(final_coin_amount) as avg_price,
                SUM(coin_bonus_amount) as bonus_sum,
                SUM(coin_coeff) as total_coins
            FROM "order"
        )
        SELECT 
            active_count,
            cancelled_count,
            done_count,
            avg_price,
            bonus_sum,
            total_coins
        FROM current_snapshot 
    """

    snapshot_data = source_hook.get_first(snapshot_sql)

    if snapshot_data:
        snapshot_insert_sql = """
            INSERT INTO OrderStatisticsSnapshots (
                snapshot_datetime,
                active_count,
                cancelled_count,
                done_count,
                avg_order_price,
                bonus_sum,
                total_coins
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        snapshot_params = (current_time,) + snapshot_data
        target_hook.run(snapshot_insert_sql, parameters=snapshot_params)


def update_processed_time(**context):
    current_time = datetime.now()
    Variable.set("marts_last_processed", str(current_time))


with DAG(
        'update_marts',
        schedule_interval='*/1 * * * *',
        default_args=default_args,
        catchup=False
) as dag:
    get_last_processed_time_task = PythonOperator(
        task_id='get_last_processed_time_task',
        python_callable=get_last_processed_time
    )

    update_executor_statistics_task = PythonOperator(
        task_id='update_executor_statistics_task',
        python_callable=update_executor_statistics,
        provide_context=True
    )

    update_order_snapshots_task = PythonOperator(
        task_id='update_order_snapshots_task',
        python_callable=update_order_snapshots,
        provide_context=True
    )

    update_processed_time_task = PythonOperator(
        task_id='update_processed_time_task',
        python_callable=update_processed_time,
        provide_context=True
    )

    get_last_processed_time_task >> [update_executor_statistics_task,
                                     update_order_snapshots_task] >> update_processed_time_task

if __name__ == "__main__":
    dag.test()
