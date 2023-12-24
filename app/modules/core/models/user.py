from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from app.common.db import metadata


class Country(SQLModel, table=True, target_metadata=metadata):
    __tablename__ = "countries"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow,
                                 sa_column_kwargs={"onupdate": datetime.utcnow})
    users: List["User"] = Relationship(back_populates="country")


class RolePermission(SQLModel, table=True, target_metadata=metadata):
    __tablename__ = "roles_permissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: int = Field(foreign_key="roles.id")
    permission_id: int = Field(foreign_key="permissions.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})


class Permission(SQLModel, table=True, target_metadata=metadata):
    __tablename__ = "permissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    roles: List["Role"] = Relationship(back_populates="permissions", link_model=RolePermission)


class UserRole(SQLModel, table=True, target_metadata=metadata):
    __tablename__ = "users_roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    role_id: int = Field(foreign_key="roles.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})


class Role(SQLModel, table=True, target_metadata=metadata):
    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    permissions: List[Permission] = Relationship(back_populates="roles", link_model=RolePermission)
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)


class User(SQLModel, table=True, target_metadata=metadata):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50)
    password_hash: str  # Length depends on hash algorithm
    name: Optional[str] = Field(default=None, max_length=50)
    surname: Optional[str] = Field(default=None, max_length=50)
    email: str = Field(max_length=255)  # Adjust max_length as needed
    country_id: int = Field(foreign_key="countries.id")
    photo_path: Optional[str] = None
    active: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow,
                                 sa_column_kwargs={"onupdate": datetime.utcnow})
    deleted_at: Optional[datetime] = None

    country: Optional[Country] = Relationship(back_populates="users", sa_relationship_kwargs={'lazy': 'joined'})
    roles: List[Role] = Relationship(back_populates="users", link_model=UserRole)
