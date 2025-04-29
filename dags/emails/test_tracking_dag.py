from pendulum import datetime
from logging import getLogger
from airflow.decorators import dag, task
from app.tasks import AppContext, set_app_context
from app.tasks.email_track import get_service, fetch_email, parse_email
from app.tasks.post_event import process_event

logger = getLogger("airflow.task")

@dag(
    dag_id="test_email_track_service",
    description="fetch and process tracking emails",
    schedule=None,
    start_date=datetime(2025, 1, 1),
)
def email_tracking_dag():
    @task
    def save_email() -> int|None:
        service = get_service()
        if service:
            logger.info("Email service authenticated")
            return fetch_email(service)
        else:
            raise Exception("Email service not availabe")

    @task
    def parse_saved_email(id: int):
        return parse_email(id)

    @task
    def add_event(app_context: AppContext):
        set_app_context(app_context)
        return process_event(app_context)

    @task(task_id="end")
    def end():
        pass

    @task.branch(task_id="check_email")
    def check_email(id: int|None) -> str:
        return "parse_saved_email" if id else "end"

    id = save_email()
    check = check_email(id)
    context = parse_saved_email(id)
    add = add_event(context)
    last = end()

    id >> check >> [context, last]
    context >> add >> last

email_tracking_dag()
