from app.core.database import Base
from sqlalchemy import (
    Integer, 
    String, 
    ForeignKey,
    DateTime, 
    Enum as SQLEnum
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from app.core.enum_data import TaskStatusEnum, TaskPriorityEnum

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    lastModified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    isAccepted: Mapped[bool] = mapped_column(nullable=False, default=False)
    
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project", 
        cascade="all, delete-orphan"
    )




class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    projectId: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), 
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[TaskStatusEnum] = mapped_column(
        SQLEnum(TaskStatusEnum),
        nullable=False, 
        default=TaskStatusEnum.TODO
    )
    priority: Mapped[TaskPriorityEnum] = mapped_column(
        SQLEnum(TaskPriorityEnum),
        nullable=False, 
        default=TaskPriorityEnum.LOW
    )
    dueDate: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    lastModified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    project: Mapped["Project"] = relationship(
        back_populates="tasks"
    )
    