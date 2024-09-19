from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.crud.user import get_users_by_emails
from app.core.models import Task, TaskStatus, User
from app.core.schemas import TaskCreate, TaskUpdate, UserSchema


@logger.catch(reraise=True)
async def check_roles_of_assigned_users(
        users: list[UserSchema],
        allowed_roles: set[str],
        position_label: str,
        session: AsyncSession
    ):
    """Compares `users` positions for compliance with `allowed roles`"""
    not_allowed_users = tuple(filter(
        lambda user: not user.role.position in allowed_roles, users
    ))
    if not_allowed_users:
        await session.close()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                ", ".join(map(str, not_allowed_users)) +
                f" cannot be assigned to a task as {position_label}. "
                f"Only «{'», «'.join(allowed_roles)}» roles "
                f"available for {position_label}."))

    return users


@logger.catch(reraise=True)
async def get_task_status_id(session: AsyncSession, status: str):
    """Retrieves task status ID from DB using specified `status` name"""
    stmt = select(TaskStatus.id).where(
        func.lower(TaskStatus.name) == status.lower())

    return await session.scalar(stmt)


@logger.catch(reraise=True)
async def get_task_by_id(session: AsyncSession, task_id: id):
    """Retrieves record about task from DB using specified `task id`"""
    stmt = (
        select(Task).where(Task.id == task_id)
        .options(
            selectinload(Task.performers)
            .joinedload(User.role)
        )
        .options(
            joinedload(Task.responsible_person)
            .joinedload(User.role)
        )
        .options(joinedload(Task.status))
        .options(joinedload(Task.priority))
        .options(
            joinedload(Task.created_by)
            .joinedload(User.role)))

    task_row = await session.scalar(stmt)
    if not task_row:
        await session.close()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Task with ID = «{task_id}» not found")

    return task_row


@logger.catch(reraise=True)
async def update_task_details(
        session: AsyncSession, task_id: int, task_in: TaskUpdate
    ):
    """
    Updates task data about responsible person, performers and
    then commit changes in database
    """
    task_to_update = await get_task_by_id(session, task_id)
    if task_in.responsible_person:
        task_to_update.responsible_person = (
            await check_roles_of_assigned_users(
                await get_users_by_emails(
                    session, [task_in.responsible_person]
                ),
                {"Project Manager", "Developer"},
                "responsible_person",
                session
            )
        )[0]

    if task_in.performers:
        task_to_update.performers = await check_roles_of_assigned_users(
            await get_users_by_emails(session, task_in.performers),
            {"Project Manager", "Developer"},
            "performers",
            session)

    await session.commit()

    return task_to_update


@logger.catch(reraise=True)
async def generate_task(
        session: AsyncSession,
        task_in: TaskCreate,
        created_by: UserSchema
    ):
    """
    Validates task data from user,
    calculates remaining fields and generates the task,
    after that saving it in database
    """
    created_task = Task(
        title=task_in.title,
        description=task_in.description,
        status_id=(
            await get_task_status_id(session, task_in.status)
        ),
        priority_id=task_in.priority,
        created_by_id=created_by.id,
        deadline=task_in.deadline
    )
    session.add(created_task)
    await session.flush()

    return await update_task_details(session, created_task.id, task_in)


@logger.catch(reraise=True)
async def update_task(
        session: AsyncSession, task_in: TaskUpdate
    ):
    """Updates task fields based on user input and saves changes to DB"""
    await session.execute(
        update(Task).where(Task.id == task_in.id)
        .values(
            title=task_in.title,
            description=task_in.description,
            status_id=(
                await get_task_status_id(session, task_in.status)
            ),
            priority_id=task_in.priority,
            deadline=task_in.deadline))

    return await update_task_details(session, task_in.id, task_in)


@logger.catch(reraise=True)
async def update_task_status(
        session: AsyncSession, task_id: int, status_name: str
    ):
    """Updates task status and save changes to database"""
    task_to_update = await get_task_by_id(session, task_id)
    new_status_id = await get_task_status_id(session, status_name)
    if task_to_update.status_id != new_status_id:
        task_to_update.status_id = new_status_id
        await session.commit()
        task_to_update.status.name = status_name

        return task_to_update


@logger.catch(reraise=True)
async def delete_task(session: AsyncSession, task_id):
    """Deletes task from DB by specified ID and returns its object"""
    task_schema = await get_task_by_id(session, task_id)
    await session.delete(task_schema)
    await session.commit()

    return task_schema


@logger.catch(reraise=True)
async def get_all_tasks(session: AsyncSession):
    """Executes query to retrieve all tasks from database"""
    stmt = (
        select(Task)
        .options(
            selectinload(Task.performers)
            .joinedload(User.role)
        )
        .options(
            joinedload(Task.responsible_person)
            .joinedload(User.role)
        )
        .options(joinedload(Task.status))
        .options(joinedload(Task.priority))
        .options(
            joinedload(Task.created_by)
            .joinedload(User.role)
        )
        .order_by(Task.created_at))

    return (await session.scalars(stmt)).all()
