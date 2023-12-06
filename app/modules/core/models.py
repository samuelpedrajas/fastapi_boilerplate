from sqlalchemy import Column, DateTime, String, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship, backref

from app.dependencies.db import Base

from app.helpers.encryption import Encryption
from datetime import datetime
from app.dependencies.config import settings

class Country(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True)
    code = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    password_hash = Column(Text, nullable=False)
    name = Column(String(255))
    surname = Column(String(255))
    email = Column(String(255), nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    photo_path = Column(String(255))
    active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    country = relationship('Country', backref=backref('users', lazy=True))
    roles = relationship('Role', secondary='users_roles', lazy='subquery', backref=backref('users', lazy=True))

    def delete(self):
        """Soft delete the user."""
        self.deleted_at = datetime.utcnow()

    @staticmethod
    def get_active_user(user_id):
        """Retrieve an active user by their ID."""
        return User.query.filter_by(id=user_id, deleted_at=None).first()

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserRole(Base):
    __tablename__ = 'users_roles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RolePermission(Base):
    __tablename__ = 'roles_permissions'

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmailTemplate(Base):
    __tablename__ = 'email_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    html_body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def render(self, user):
        # Mapping known variables
        variables = {
            '@@name@@': user.name,
            '@@surname@@': user.surname,
            '@@username@@': user.username,
            '@@confirmation_url@@': self.generate_confirmation_url(user)
        }

        # Replacing variables in the template
        rendered_body = self.html_body
        for var, value in variables.items():
            if value is not None:
                rendered_body = rendered_body.replace(var, value)
            else:
                rendered_body = rendered_body.replace(var, '')

        return rendered_body

    @staticmethod
    def generate_confirmation_url(user):
        encryption = Encryption(settings.SECRET_KEY)
        token = encryption.encrypt(str(user.id))
        # Generate the URL dynamically
        confirmation_url = f"http://localhost:8000/auth/confirm/?token={token}"
        return confirmation_url


class EmailVariable(Base):
    __tablename__ = 'email_variables'

    id = Column(Integer, primary_key=True)
    variable = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
