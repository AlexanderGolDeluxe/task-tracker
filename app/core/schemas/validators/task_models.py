from fastapi import Form, HTTPException, status
from loguru import logger

from app.config import TASK_PRIORITY_LABELS, TASK_STATUSES

task_priority_levels = {
    label.lower(): level for level, label in TASK_PRIORITY_LABELS.items()
}


@logger.catch(reraise=True)
def check_task_priority(priority_name: str):
    """
    Validates accordance
    between user input of task `priority name` and supported priorities.
    Converts a priority label to its corresponding ID from database
    """
    task_priority_level = task_priority_levels.get(priority_name.lower())
    if task_priority_level is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Task priority must be one of: "
                f"«{'», «'.join(TASK_PRIORITY_LABELS.values())}»"))

    return task_priority_level


@logger.catch(reraise=True)
def check_task_status(status_name: str = Form(
        examples=["In progress"],
        description=f"Choose one of this: «{'», «'.join(TASK_STATUSES)}»"
    )):
    """
    Validates accordance
    between user input of task `status name` and supported statuses
    """
    if not status_name.lower() in set(map(str.lower, TASK_STATUSES)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Task status must be one of: "
                f"«{'», «'.join(TASK_STATUSES)}»"))

    return status_name
