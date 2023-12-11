from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from .country import Country
from .role import Role
from app.common.db import metadata


class UserRole(SQLModel, table=True, target_metadata=metadata):
    __tablename__ = "users_roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    role_id: int = Field(foreign_key="roles.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})


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

    country: Optional[Country] = Relationship(back_populates="users")
    roles: List[Role] = Relationship(back_populates="users", link_model=UserRole)
