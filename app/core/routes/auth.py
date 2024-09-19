from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import API_PREFIX
from app.configuration.db_helper import db_helper
from app.core.schemas import TokenInfo, UserSchema
from app.utils.auth_jwt import (
    encode_jwt, get_current_token_payload, validate_auth_user
)
from app.core.crud.user import get_user_by_login

router = APIRouter(prefix=API_PREFIX + "/auth", tags=["auth"])


@logger.catch(reraise=True)
async def get_current_auth_user(
        payload: dict = Depends(get_current_token_payload),
        session: AsyncSession = Depends(
            db_helper.scoped_session_dependency)
    ):
    user_login = payload.get("sub")

    return await get_user_by_login(session, user_login)


class RoleChecker:  
    def __init__(self, allowed_roles: set[str]):  
        self.allowed_roles = allowed_roles

    def __call__(
            self, user: UserSchema = Depends(get_current_auth_user)
        ):
        if not user.role.position in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Access to this route is only possible for roles: "
                    f"«{'», «'.join(self.allowed_roles)}»"))

        return user


@router.post("/jwt/login", response_model=TokenInfo)
async def auth_user_issue_jwt(
        user: UserSchema = Depends(validate_auth_user)
    ):
    jwt_payload = dict(
        sub=user.login,
        username=user.login,
        role=user.role.position
    )
    token = encode_jwt(jwt_payload)

    return TokenInfo(access_token=token, token_type="Bearer")
