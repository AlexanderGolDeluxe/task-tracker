from typing import Annotated

from pydantic import (
    BaseModel, ConfigDict, EmailStr, Field, NonNegativeInt, SecretStr)

from app.core.schemas import RolePermissionSchema


class UserBase(BaseModel):
    model_config = ConfigDict(strict=True)

    login: Annotated[str, Field(min_length=3, max_length=50)]
    email: Annotated[EmailStr, Field(min_length=3, max_length=50)]
    password: Annotated[bytes, Field(exclude=True)]
    role: NonNegativeInt | None


class UserCreate(UserBase):
    password: Annotated[SecretStr, Field(min_length=8)]
    role: str


class UserSchema(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: RolePermissionSchema | None


class TokenInfo(BaseModel):
    access_token: str
    token_type: str = "Bearer"
