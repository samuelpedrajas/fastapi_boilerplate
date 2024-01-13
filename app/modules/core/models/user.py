from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, Relationship
from app.common.db import metadata
from app.common.base_model import BaseModel


class Country(BaseModel, table=True, target_metadata=metadata):
    __tablename__ = "countries"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    name: str

    users: List["User"] = Relationship(back_populates="country")


class RolePermission(BaseModel, table=True, target_metadata=metadata):
    __tablename__ = "roles_permissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: int = Field(foreign_key="roles.id")
    permission_id: int = Field(foreign_key="permissions.id")


class Permission(BaseModel, table=True, target_metadata=metadata):
    __tablename__ = "permissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    roles: List["Role"] = Relationship(back_populates="permissions", link_model=RolePermission)


class UserRole(BaseModel, table=True, target_metadata=metadata):
    __tablename__ = "users_roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    role_id: int = Field(foreign_key="roles.id")


class Role(BaseModel, table=True, target_metadata=metadata):
    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    permissions: List[Permission] = Relationship(back_populates="roles", link_model=RolePermission)
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)


class User(BaseModel, table=True, target_metadata=metadata):
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
    deleted_at: Optional[datetime] = None

    country: Optional[Country] = Relationship(back_populates="users")
    roles: List[Role] = Relationship(back_populates="users", link_model=UserRole)
