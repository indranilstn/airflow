from airflow.decorators import dag, task
from airflow.models.param import Param
from pendulum import datetime
from logging import getLogger

from app.tasks.email_track import get_service, fetch_email

@dag(
    dag_id="lt_email_track_service",
    description="fetch and process tracking emails",
    schedule=None,
    start_date=datetime(2025, 1, 1),
    params={
        'file_path': Param(
            default=None,
            type=["null", "string"],
            description="Path of a raw email file"
        )
    }
)
def email_tracking_dag():
    @task
    def save_emails(**context):
        logger = getLogger(__name__)

        params = context.get("params")
        file_path = params.get("file_path") or ""

        service = get_service(file_path=file_path)
        if service:
            logger.info("Email service authenticated")
            fetch_email(service)
        else:
            raise Exception("Email service not availabe")

    save_emails()

email_tracking_dag()
