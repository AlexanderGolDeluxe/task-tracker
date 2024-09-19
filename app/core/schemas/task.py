from datetime import datetime
from typing import Annotated

from pydantic import (
    BeforeValidator,
    BaseModel,
    EmailStr,
    Field,
    FutureDatetime,
    NonNegativeInt)

from app.config import TASK_PRIORITY_LABELS, TASK_STATUSES
from app.core.schemas import UserSchema
from app.core.schemas.validators import (
    check_task_priority, check_task_status
)
from app.utils.work_with_dates import parse_like_datetime


class TaskStatusCreate(BaseModel):
    name: str


class TaskStatusSchema(TaskStatusCreate):
    id: int


class TaskPriorityCreate(BaseModel):
    name: Annotated[str, Field(max_length=50)]
    importance_level: NonNegativeInt


class TaskPrioritySchema(TaskPriorityCreate):
    id: int


class TaskCreate(BaseModel):
    title: Annotated[str, Field(max_length=250)]
    description: str | None = None
    responsible_person: EmailStr
    performers: Annotated[
        list[EmailStr],
        Field(examples=[["user@example.com"]]),
        BeforeValidator(lambda emails: list(filter(None, emails)))
    ] = list()
    status: Annotated[
        str,
        Field(examples=TASK_STATUSES),
        BeforeValidator(check_task_status)
    ] = "TODO"
    priority: Annotated[
        NonNegativeInt,
        Field(examples=list(TASK_PRIORITY_LABELS.values())),
        BeforeValidator(check_task_priority)
    ] = 5
    deadline: Annotated[
        FutureDatetime | None,
        Field(examples=[datetime.now().strftime("%d.%m.%Y %H:%M")]),
        BeforeValidator(parse_like_datetime)] = None


class TaskUpdate(TaskCreate):
    id: int


class TaskSchema(TaskCreate):
    id: int
    responsible_person: UserSchema | None
    performers: list[UserSchema | None]
    status: TaskStatusSchema
    priority: TaskPrioritySchema
    created_at: datetime
    created_by: UserSchema
    deadline: datetime | None
