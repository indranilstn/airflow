from airflow.decorators import dag, task
from pendulum import datetime
from logging import getLogger

from include.tasks.email_track import get_service, fetch_email

@dag(
    dag_id="test_email_track_service",
    description="fetch and process tracking emails",
    schedule=None,
    start_date=datetime(2025, 1, 1),
)
def email_tracking_dag():
    @task
    def save_emails():
        logger = getLogger(__name__)
        service = get_service()
        if service:
            logger.info("Email service authenticated")
            fetch_email(service)
        else:
            raise Exception("Email service not availabe")

    save_emails()

email_tracking_dag()
