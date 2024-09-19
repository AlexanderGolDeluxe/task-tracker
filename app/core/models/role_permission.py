from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base

if TYPE_CHECKING:
    from app.core.models import User


class RolePermission(Base):
    __tablename__ = "role_permission"

    position = mapped_column(String(100), unique=True)
    description_of_access_to_actions: Mapped[str | None]
    assigned_users: Mapped[list["User"] | None] = relationship(
        back_populates="role")
