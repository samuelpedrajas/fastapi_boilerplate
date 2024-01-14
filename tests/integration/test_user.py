import os
import pytest
from sqlalchemy import func, insert
from sqlalchemy.orm import selectinload
from sqlmodel import select
from config import settings
from unittest import mock
from app.helpers.security import encrypt
from app.modules.core.models.user import User, UserRole, Role
from app.helpers.security import get_password_hash
from tests.conftest import (
    app,
    test_client,
    current_transaction,
    async_engine,
    DEFAULT_COUNTRIES,
    setup_db,
    get_access_token,
)

DEFAULT_USER = [
    {
        'username': 'test',
        'password_hash': get_password_hash('testpassword'),
        'name': 'Test',
        'surname': 'User',
        'email': 'test@test.com',
        'country_id': 1,
        'active': True
    }
]


@pytest.fixture(scope="module", autouse=True)
async def setup_db(async_engine, setup_db):
    async with async_engine.begin() as conn:
        stmt = insert(User).values(DEFAULT_USER).returning(User.id)
        result = await conn.execute(stmt)
        user_ids = [row[0] for row in result.fetchall()]
        user_id = user_ids[0]
        DEFAULT_USER[0]['id'] = user_id

        stmt = select(Role.id).where(Role.name == 'admin')
        result = await conn.execute(stmt)
        role_id = result.fetchone()[0]

        await conn.execute(
            insert(UserRole),
            {'user_id': user_id, 'role_id': role_id}
        )

    yield


@pytest.mark.asyncio
async def test_get_user(app, test_client, current_transaction):
    user = (
        await current_transaction.exec(
            select(User)
                .options(selectinload(User.roles))
                .where(User.id == DEFAULT_USER[0]['id'])
        )
    ).unique().one()
    token = get_access_token(user)
    response = await test_client.get(
        app.url_path_for('user.get_user', user_id=user.id),
        headers={'Authorization': f'Bearer {token}'}
    )

    # check the response
    assert response.status_code == 200

    json_response = response.json()
    expected_result = {
        'id': user.id,
        'username': user.username,
        'name': user.name,
        'surname': user.surname,
        'email': user.email,
        'country': {
            'id': 1,
            'name': DEFAULT_COUNTRIES[0]['name'],
            'code': DEFAULT_COUNTRIES[0]['code']
        },
    }
    assert json_response == {'status': 200, 'message': None, 'result': expected_result}
