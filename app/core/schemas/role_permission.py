from pydantic import BaseModel


class RolePermissionCreate(BaseModel):
    position: str
    description_of_access_to_actions: str | None = None


class RolePermissionSchema(RolePermissionCreate):
    id: int
