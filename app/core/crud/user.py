from fastapi import Form, HTTPException, status
from loguru import logger
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.config import ROLE_PERMISSIONS
from app.core.crud.role_permission import get_role_permission
from app.core.models import User
from app.core.schemas import UserCreate, UserSchema
from app.utils import auth_jwt as auth_utils


@logger.catch(reraise=True)
def validate_creating_user(
        login: str = Form(min_length=3),
        email: str = Form(min_length=3),
        password: SecretStr = Form(min_length=8),
        role: str = Form(
            examples=["Developer"],
            description="Choose one of this: «" +
            "», «".join(ROLE_PERMISSIONS.keys()) + "»")
    ):
    """Validates auth data entered by user using the pydantic model"""
    return UserCreate(
        login=login, email=email, password=password, role=role)


@logger.catch(reraise=True)
async def create_user(session: AsyncSession, user_in: UserCreate):
    """
    Inserts new user into database (table `user`) or raises exception
    if user with the same login or email already exists
    """
    role_permission = await get_role_permission(session, user_in.role)
    user = User(
        login=user_in.login,
        email=user_in.email,
        password=auth_utils.hash_password(user_in.password),
        role_permission_id=role_permission.id
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "User with the same login or email already exists. "
                "Please, choose another one"))
    finally:
        await session.close()

    created_user = UserSchema(
        id=user.id,
        login=user.login,
        email=user.email,
        password=user.password,
        role=role_permission)

    return created_user


@logger.catch(reraise=True)
async def get_user_by_login(session: AsyncSession, login: str):
    """Retrieves record about user from DB using specified `login`"""
    stmt = (
        select(User)
        .options(joinedload(User.role))
        .where(User.login == login))

    return await session.scalar(stmt)


@logger.catch(reraise=True)
async def get_users_by_emails(session: AsyncSession, emails: list[str]):
    """Retrieves users from database using specified `emails`"""
    stmt = (
        select(User).options(joinedload(User.role))
        .where(User.email.in_(emails))
    )
    users = (await session.scalars(stmt)).all()
    not_finded_emails = set(emails).difference(
        set(user.email for user in users)
    )
    if not_finded_emails:
        plural = "s" if len(not_finded_emails) > 1 else ""
        await session.close()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"User{plural} with email{plural} "
                f"«{'», «'.join(not_finded_emails)}» not found"))

    return users
