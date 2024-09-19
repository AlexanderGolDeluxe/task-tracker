from fastapi import (
    APIRouter, BackgroundTasks, Depends, Form, HTTPException, status
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import API_PREFIX
from app.configuration.db_helper import db_helper
from app.core.crud.task import (
    delete_task,
    generate_task,
    get_all_tasks,
    update_task,
    update_task_status
)
from app.core.routes.auth import RoleChecker
from app.core.schemas import (
    TaskCreate, TaskSchema, TaskUpdate, UserSchema
)
from app.core.schemas.validators import check_task_status
from app.utils.email_sender import notify_about_change_task_status

router = APIRouter(prefix=API_PREFIX + "/task", tags=["task"])


@router.post("/create", response_model=TaskSchema, status_code=201)
async def create_task(
        task_in: TaskCreate,
        user: UserSchema = Depends(
            RoleChecker({"Owner", "Admin", "Project Manager"})
        ),
        session: AsyncSession = Depends(
            db_helper.scoped_session_dependency)):

    return await generate_task(session, task_in, user)


@router.put("/edit", response_model=TaskSchema)
async def edit_task(
        task_in: TaskUpdate,
        user: UserSchema = Depends(
            RoleChecker({"Owner", "Admin", "Project Manager"})
        ),
        session: AsyncSession = Depends(
            db_helper.scoped_session_dependency)):

    return await update_task(session, task_in)


@router.patch("/change_task_status", response_model=TaskSchema)
async def change_task_status(
        background_tasks: BackgroundTasks,
        task_id: int = Form(ge=1),
        status_name: str = Depends(check_task_status),
        user: UserSchema = Depends(
            RoleChecker({"Admin", "Project Manager", "Developer"})
        ),
        session: AsyncSession = Depends(
            db_helper.scoped_session_dependency)):

    updated_task = await update_task_status(
        session, task_id, status_name
    )
    if updated_task is None:
        await session.close()
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail=f"Task is already in «{status_name}» status")

    notify_about_change_task_status(updated_task, user, background_tasks)

    return updated_task

@router.delete("/remove", response_model=TaskSchema)
async def remove_task(
        task_id: int = Form(ge=1),
        user: UserSchema = Depends(
            RoleChecker({"Owner", "Admin", "Project Manager"})
        ),
        session: AsyncSession = Depends(
            db_helper.scoped_session_dependency)):

    return await delete_task(session, task_id)


@router.get("/retrieve", response_model=list[TaskSchema])
async def get_tasks(session: AsyncSession = Depends(
            db_helper.scoped_session_dependency)):

    return await get_all_tasks(session)
