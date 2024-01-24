from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.common.base_model import BaseModel


class Country(BaseModel):
    __tablename__ = "countries"

    code = Column(String)
    name = Column(String)

    users = relationship("User", back_populates="country")


class RolePermission(BaseModel):
    __tablename__ = "roles_permissions"

    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id'), primary_key=True)


class Permission(BaseModel):
    __tablename__ = "permissions"

    name = Column(String)

    roles = relationship("Role", secondary="roles_permissions", back_populates="permissions")


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String)

    permissions = relationship("Permission", secondary="roles_permissions", back_populates="roles")
    users = relationship("User", secondary="users_roles", back_populates="roles")


class UserRole(BaseModel):
    __tablename__ = "users_roles"

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True)
    password_hash = Column(String)
    name = Column(String(50), nullable=True)
    surname = Column(String(50), nullable=True)
    email = Column(String(255), unique=True)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=True)
    photo_path = Column(String, nullable=True)
    active = Column(Boolean, default=False)

    country = relationship("Country", back_populates="users")
    roles = relationship("Role", secondary="users_roles", back_populates="users")
