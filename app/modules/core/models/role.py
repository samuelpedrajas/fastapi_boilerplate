from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from .permission import Permission
from app.common.db import metadata


class RolePermission(SQLModel, table=True, target_metadata=metadata):
    __tablename__ = "roles_permissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: int = Field(foreign_key="roles.id")
    permission_id: int = Field(foreign_key="permissions.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})


class Role(SQLModel, table=True, target_metadata=metadata):
    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    permissions: List[Permission] = Relationship(back_populates="roles", link_model=RolePermission)
