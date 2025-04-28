from contextvars import ContextVar
from typing import TypedDict, NotRequired, Any
from airflow.decorators import task
from airflow.utils.trigger_rule import TriggerRule

class AppContext(TypedDict):
    client: str|None
    data: NotRequired[dict|None]

def get_branch_task_id(branched_task: str, context: dict[str, Any]) -> str:
    task_instance = context['ti']
    group_id = task_instance.task.task_group.group_id if task_instance.task.task_group else None
    branched_task_id = f"{group_id}.{branched_task}" if group_id else branched_task

    return branched_task_id


def get_branch_result_task(*, task_id: str = "branch_result", branch_task: str):
    def task_func(**context):
        task_instance = context['ti']
        group_id = task_instance.task.task_group.group_id if task_instance.task.task_group else None
        branch_task_id = f"{group_id}.{branch_task}" if group_id else branch_task
        branched_task_id = task_instance.xcom_pull(task_ids=branch_task_id)

        result = None
        if branched_task_id:
            print(f"Task id: {branched_task_id}")
            result = task_instance.xcom_pull(task_ids=branched_task_id)

        return result

    return task(
        task_id=task_id,
        trigger_rule=TriggerRule.ONE_SUCCESS
    )(task_func)


CONTEXT_KEY = "app_context"
_app_context = None

def set_app_context(context: AppContext) -> None:
    global _app_context
    _app_context = ContextVar(CONTEXT_KEY, default=context)


def get_app_context() -> ContextVar|None:
    global _app_context
    return _app_context
