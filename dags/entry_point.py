from os import getenv
from pendulum import datetime
from logging import getLogger
from airflow.decorators import dag, task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from sqlalchemy import select, update
from app.orm import get_pg_session
from app.orm.models.service_requests import ServiceRequest
from app.services.service_locator import find_service

logger = getLogger("airflow.task")

@dag(
    dag_id="service_entry_point",
    description="Entry point for all triggered dags",
    schedule=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    params={
        'id': None
    }
)
def trigger_entry():
    @task
    def get_request_data(**context) -> ServiceRequest|None:
        params = context['params']
        id = params.get('id')

        connection_id = getenv('APP__DATABASE__CONN_ID')
        with get_pg_session(connection_id=connection_id) as session:
            request = session.scalar(
                select(ServiceRequest)
                .where(ServiceRequest.id == id)
            )
            if request:
                logger.info(f"Service request received for id: {id}")
            else:
                raise Exception(f"Service request not found for id: {id}")

        dag_id = find_service(request)
        if dag_id:
            print(f"Triggering dag: {dag_id}")
            return {
                'id': dag_id,
                'data': request.data,
            }
        else:
            raise Exception(f"No service registered for request id: {id}")

    trigger_task = TriggerDagRunOperator(
        task_id="trigger_service_dag",
        trigger_dag_id='{{ ti.xcom_pull(task_ids="get_request_data")["id"] }}',
        conf={
            'data': '{{ ti.xcom_pull(task_ids="get_request_data")["data"] }}'
        },
        wait_for_completion=False,
    )

    @task
    def mark_processed(**context) -> None:
        params = context['params']
        id = params.get('id')

        connection_id = getenv('APP__DATABASE__CONN_ID')
        with get_pg_session(connection_id=connection_id) as session:
            session.execute(
                update(ServiceRequest)
                .where(ServiceRequest.id == id)
                .values(is_processed=True)
            )

    start_task = get_request_data()
    end_task = mark_processed()

    start_task >> trigger_task >> end_task

trigger_entry()
