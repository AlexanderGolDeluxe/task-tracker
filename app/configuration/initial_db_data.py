from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import (
    ROLE_PERMISSIONS, TASK_PRIORITY_LABELS, TASK_STATUSES
)
from app.configuration.db_helper import db_helper
from app.core.models import RolePermission, TaskPriority, TaskStatus
from app.core.schemas import (
    RolePermissionCreate, TaskPriorityCreate, TaskStatusCreate)


@logger.catch(reraise=True)
async def insert_role_permissions(session: AsyncSession):
    """Add initial role permissions to DB"""
    stmt = select(RolePermission.position)
    existing_permissions = {
        row[0] for row in (await session.execute(stmt))
    }
    necessary_permissions = {
        role: desc for role, desc in ROLE_PERMISSIONS.items()
        if not role in existing_permissions
    }
    if necessary_permissions:
        session.add_all(
            RolePermission(**RolePermissionCreate(
                position=role, description_of_access_to_actions=desc
            ).model_dump())
            for role, desc in necessary_permissions.items()
        )
        await session.commit()


@logger.catch(reraise=True)
async def insert_task_priorities(session: AsyncSession):
    """Add initial task priorities to DB"""
    stmt = select(TaskPriority.name)
    existing_priorities = {
        row[0] for row in (await session.execute(stmt))
    }
    necessary_priorities = {
        level: label for level, label in TASK_PRIORITY_LABELS.items()
        if not label in existing_priorities
    }
    if necessary_priorities:
        session.add_all(
            TaskPriority(**TaskPriorityCreate(
                importance_level=level, name=label
            ).model_dump())
            for level, label in necessary_priorities.items()
        )
        await session.commit()


@logger.catch(reraise=True)
async def insert_task_statuses(session: AsyncSession):
    """Add initial task statuses to DB"""
    stmt = select(TaskStatus.name)
    existing_statuses = {
        row[0] for row in (await session.execute(stmt))
    }
    necessary_statuses = tuple(filter(
        lambda status: not status in existing_statuses, TASK_STATUSES
    ))
    if necessary_statuses:
        session.add_all(
            TaskStatus(**TaskStatusCreate(name=status).model_dump())
            for status in necessary_statuses
        )
        await session.commit()


@logger.catch(reraise=True)
async def insert_all_initial_db_data():
    """
    Fill DB with initial data for correct functioning of app
    """
    session = db_helper.get_scoped_session()
    await insert_role_permissions(session)
    await insert_task_priorities(session)
    await insert_task_statuses(session)
    await session.close()
