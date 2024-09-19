from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base

if TYPE_CHECKING:
    from app.core.models import User

task_user_association_table = Table(
    "task_user_association",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "task_id",
        ForeignKey("task.id", ondelete="CASCADE"),
        nullable=False
    ),
    Column(
        "user_id",
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    ),
    UniqueConstraint("task_id", "user_id", name="idx_unique_task_user")
)


class TaskStatus(Base):
    __tablename__ = "task_status"

    name = mapped_column(String(50), unique=True)


class TaskPriority(Base):
    __tablename__ = "task_priority"

    name = mapped_column(String(50), unique=True)
    importance_level: Mapped[int] = mapped_column(unique=True)


class Task(Base):
    __tablename__ = "task"

    title = mapped_column(String(250))
    description: Mapped[str | None]
    responsible_person_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL")
    )
    responsible_person: Mapped["User"] = relationship(
        foreign_keys=[responsible_person_id]
    )
    performers: Mapped[list["User"]] = relationship(
        secondary=task_user_association_table,
        back_populates="assigned_tasks"
    )
    status_id: Mapped[int] = mapped_column(
        ForeignKey("task_status.id"), default=1, server_default="1"
    )
    status: Mapped[TaskStatus] = relationship()
    priority_id: Mapped[int | None] = mapped_column(
        ForeignKey("task_priority.id"), default=5, server_default="5"
    )
    priority: Mapped[TaskPriority] = relationship()
    created_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_by: Mapped["User"] = relationship(
        foreign_keys=[created_by_id]
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    deadline: Mapped[datetime | None] = mapped_column(
        CheckConstraint("deadline > CURRENT_TIMESTAMP"))
