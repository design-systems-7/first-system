'''
A simple DAG to check if airflow is working properly.
'''

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from datetime import datetime

# Define a function to print the result
def print_result(**context):
    # Retrieve the result from XCom
    result = context['ti'].xcom_pull(task_ids='count_entries')
    print(f"Total number of entries in the database: {result[0][0]}")

# Define the DAG
with DAG(
    dag_id="count_db_entries",
    start_date=datetime(2024, 12, 1),  # Replace with an appropriate start date
    schedule_interval=None,  # Run manually
    catchup=False,
) as dag:

    # Task 1: Count entries in the database
    count_entries = PostgresOperator(
        task_id="count_entries",
        postgres_conn_id="first_service",  # Connection ID defined in Airflow
        sql='SELECT COUNT(*) FROM "order";',  # Replace with your table name
    )

    # Task 2: Print the result
    print_result_task = PythonOperator(
        task_id="print_result",
        python_callable=print_result,
        provide_context=True,
    )

    # Define task dependencies
    count_entries >> print_result_task
