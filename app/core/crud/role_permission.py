from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ROLE_PERMISSIONS
from app.core.models import RolePermission
from app.core.schemas import RolePermissionSchema


@logger.catch(reraise=True)
async def get_role_permission(session: AsyncSession, role_name: str):
    """
    Retrieves record about role permission from database
    using specified `role_name`
    """
    role_permission_row = await session.scalar(
        select(RolePermission).where(
            func.lower(RolePermission.position) == role_name.lower())
    )
    if not role_permission_row:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Role permission must be one of: "
                f"«{'», «'.join(ROLE_PERMISSIONS)}»"))

    return RolePermissionSchema.model_validate(
        role_permission_row, from_attributes=True)
