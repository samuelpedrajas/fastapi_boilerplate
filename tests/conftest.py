import logging
import os
from typing import AsyncIterator
from unittest import mock
import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient
from sqlalchemy import NullPool, insert
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from config import settings
from app.modules.core.models.user import Country, Role, Permission, RolePermission, User
from app.modules.core.models.email_template import EmailTemplate, EmailTemplateEmailVariable, EmailVariable
from app.common.db import get_db, Base
from app import create_app
from app.modules.core.services.auth_service import AuthService


# Define the default data
DEFAULT_COUNTRIES = [
    {'name': 'Country1', 'code': 'C1'},
    {'name': 'Country2', 'code': 'C2'},
]

DEFAULT_ROLES = [
    {'name': 'user'},
    {'name': 'admin'},
]

DEFAULT_PERMISSIONS = [
    {"name": "base"},
    {"name": "admin"},
]

DEFULT_ROLES_PERMISSIONS = [
    {"role_id": 1, "permission_id": 1},
    {"role_id": 2, "permission_id": 1},
    {"role_id": 2, "permission_id": 2},
]

DEFAULT_EMAIL_TEMPLATES = [
    {
        'name': 'account_confirmation',
        'subject': 'Please, confirm your email address',
        'html_body': '<p>Hi @@name@@,</p><p>Click <a href="@@confirmation_url@@">here</a> to confirm your email address.</p>',
    },
    {
        'name': 'password_reset',
        'subject': 'Reset your password',
        'html_body': '<p>Hi @@name@@,</p><p>Click <a href="@@password_reset_url@@">here</a> to reset your password.</p>',
    },
]

DEFAULT_EMAIL_VARIABLES = [
    {'variable': 'name', 'description': 'The name of the user'},
    {'variable': 'surname', 'description': 'The surname of the user'},
    {'variable': 'confirmation_url', 'description': 'The URL to confirm the user email address'},
    {'variable': 'password_reset_url', 'description': 'The URL to reset the user password'},
]

DEFAULT_EMAIL_TEMPLATES_EMAIL_VARIABLES = [
    {'email_template_id': 1, 'email_variable_id': 1},
    {'email_template_id': 1, 'email_variable_id': 2},
    {'email_template_id': 1, 'email_variable_id': 3},
    {'email_template_id': 2, 'email_variable_id': 1},
    {'email_template_id': 2, 'email_variable_id': 2},
    {'email_template_id': 2, 'email_variable_id': 4},
]


@pytest.fixture(scope="session")
async def async_engine():
    async_engine = create_async_engine(settings.sqlalchemy_test_database_url, poolclass=NullPool)

    yield async_engine

    await async_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def setup_db(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(insert(Country), DEFAULT_COUNTRIES)
        await conn.execute(insert(Role), DEFAULT_ROLES)
        await conn.execute(insert(Permission), DEFAULT_PERMISSIONS)
        await conn.execute(insert(RolePermission), DEFULT_ROLES_PERMISSIONS)
        await conn.execute(insert(EmailTemplate), DEFAULT_EMAIL_TEMPLATES)
        await conn.execute(insert(EmailVariable), DEFAULT_EMAIL_VARIABLES)
        await conn.execute(insert(EmailTemplateEmailVariable), DEFAULT_EMAIL_TEMPLATES_EMAIL_VARIABLES)

    yield

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def app():
    with mock.patch('app.modules.core.services.file_service.FileService.save_file') as mock_save_file:
        mock_save_file.return_value = 'testobject'
        with mock.patch('app.modules.core.services.file_service.FileService.delete_file') as mock_delete_file:
            mock_save_file.mock_delete_file = True
            yield create_app()


@pytest.fixture(scope="function")
async def test_client(app):
    async with AsyncClient(app=app, base_url=settings.SERVER_URL) as client:
        yield client


@pytest.fixture(scope="function")
async def current_transaction(async_engine, app, setup_db):
    async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        # mock the commit method to flush instead
        session.commit = AsyncMock(side_effect=session.flush)

        # share the session with the app
        async def override_get_db() -> AsyncIterator[AsyncSession]:
            yield session
        app.dependency_overrides[get_db] = override_get_db

        async with session.begin() as transaction:
            yield session
            await transaction.rollback()


def get_access_token(user: User):
    return AuthService.create_access_token(user)
