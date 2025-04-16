import logging
from datetime import datetime, timedelta
from airflow.decorators import dag, task, task_group
from app.tasks import get_branch_result_task, get_branch_task_id

logger = logging.getLogger("airflow.task")

@dag(
    dag_id="my_example_dag",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "email": ["indranil@softechnation.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'sla': timedelta(hours=2),
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'on_skipped_callback': another_function, #or list of functions
        # 'trigger_rule': 'all_success'
    },
    description="A simple test DAG",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["example"],
)
def my_example_dag_func():

    @task
    def start():
        print("In start")
        return {'data': "Some data"}

    @task_group(group_id="my_group")
    def group(data: dict):
        print("In group")
        logger.info("In group")

        @task.branch(task_id="branch")
        def branch(**context):
            print("In branch")
            logger.info("In branch")

            return get_branch_task_id("first", context)

        @task(task_id="first")
        def first(data: dict):
            print("In first")
            logger.info("In first")
            return data

        @task(task_id="second")
        def second(data: dict, **context):
            print("In second")
            print(context)
            logger.info("In second")
            return data

        br_task = branch()

        fi_task = first(data)
        se_task = second(data)
        re_task = get_branch_result_task(branch_task="branch")()

        result = (br_task >> [fi_task, se_task] >> re_task)

        return result

    @task
    def end(data):
        print("In end")
        logger.info("In end")

        return data

    s_output = start()
    gr_task = group(s_output)
    end(gr_task)

my_example_dag_func()
