from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base

from app.core.models import task_user_association_table
if TYPE_CHECKING:
    from app.core.models import RolePermission, Task


class User(Base):
    __tablename__ = "user"

    login: Mapped[str] = mapped_column(
        String(50), unique=True, index=True
    )
    email: Mapped[str] = mapped_column(
        String(50), unique=True, index=True
    )
    password: Mapped[bytes]
    role_permission_id: Mapped[int | None] = mapped_column(
        ForeignKey("role_permission.id", ondelete="SET NULL")
    )
    role: Mapped["RolePermission"] = relationship(
        back_populates="assigned_users"
    )
    assigned_tasks: Mapped[list["Task"]] = relationship(
        secondary=task_user_association_table,
        back_populates="performers")

    def __str__(self):
        return (
            f"{self.__class__.__name__}"
            f"(id={self.id}, login={self.login!r}, email={self.email!r},"
            f" role={self.role.position!r})")

    def __repr__(self):
        return str(self)
