from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from country import Country
from role import Role


class UserRole(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    role_id: int = Field(foreign_key="role.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50)
    password_hash: str  # Length depends on hash algorithm
    name: Optional[str] = Field(default=None, max_length=50)
    surname: Optional[str] = Field(default=None, max_length=50)
    email: str = Field(max_length=255)  # Adjust max_length as needed
    country_id: int = Field(foreign_key="country.id")
    photo_path: Optional[str] = None
    active: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow,
                                 sa_column_kwargs={"onupdate": datetime.utcnow})
    deleted_at: Optional[datetime] = None

    country: Optional[Country] = Relationship(back_populates="users")
    roles: List[Role] = Relationship(back_populates="users", link_model=UserRole)
