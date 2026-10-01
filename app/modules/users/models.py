from app.core.database import Base
from sqlalchemy import (
    Integer, 
    String, 
    DateTime, 
    ForeignKey, 
    Column, 
    Table,
    Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app.core.enum_data import PermissionEnum
from sqlalchemy import Enum as SQLEnum


users_permissions = Table(
    "users_permissions",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"


    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    fullname: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    has_permissions: Mapped[list["Permission"]] = relationship(
        secondary=users_permissions,
        back_populates="users",
    )
    
    
class Permission(Base):
    __tablename__ = "permissions"


    id: Mapped[int] = mapped_column(primary_key=True)
    permission: Mapped[PermissionEnum] = mapped_column(
        SQLEnum(PermissionEnum),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    users: Mapped[list["User"]] = relationship(
        secondary=users_permissions,
        back_populates="has_permissions",
    )
    