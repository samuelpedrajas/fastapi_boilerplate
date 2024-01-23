import os
import pytest
from sqlalchemy import func, insert, select
from sqlalchemy.orm import selectinload
from config import settings
from unittest import mock
from app.common.security import encrypt
from app.modules.core.models.user import User, UserRole, Role
from app.common.security import get_password_hash
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


@pytest.fixture(scope="function")
async def setup_db(async_engine, current_transaction):
    stmt = insert(User).values(DEFAULT_USER).returning(User.id)
    result = await current_transaction.execute(stmt)
    user_id = result.fetchall()[0][0]
    DEFAULT_USER[0]['id'] = user_id

    stmt = select(Role.id).where(Role.name == 'admin')
    result = await current_transaction.execute(stmt)
    role_id = result.fetchall()[0][0]

    stmt = insert(UserRole).values(
        {'user_id': user_id, 'role_id': role_id}
    )
    await current_transaction.execute(stmt)

    yield


@pytest.mark.asyncio
async def test_get_user(app, test_client, current_transaction, setup_db):
    user = (
        await current_transaction.execute(
            select(User)
                .options(selectinload(User.roles))
                .where(User.id == DEFAULT_USER[0]['id'])
        )
    ).unique().one()[0]
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
        'photo_url': None,
    }
    assert json_response == {'status': 200, 'message': None, 'result': expected_result}


@pytest.mark.asyncio
async def test_put_user(app, test_client, current_transaction, setup_db):
    user = (
        await current_transaction.execute(
            select(User)
                .options(selectinload(User.roles))
                .where(User.id == DEFAULT_USER[0]['id'])
        )
    ).unique().one()[0]
    token = get_access_token(user)
    data = {
        'name': 'Test2',
        'surname': 'User2',
        'country_id': 2,
    }

    response = await test_client.put(
        app.url_path_for('user.put_user', user_id=user.id),
        headers={'Authorization': f'Bearer {token}'},
        data=data
    )

    # check the response
    assert response.status_code == 200

    json_response = response.json()
    expected_result = {
        'id': user.id,
        'username': user.username,
        'name': data['name'],
        'surname': data['surname'],
        'email': user.email,
        'country': {
            'id': 2,
            'name': DEFAULT_COUNTRIES[1]['name'],
            'code': DEFAULT_COUNTRIES[1]['code']
        },
        'photo_url': None,
    }

    assert json_response == {'status': 200, 'message': None, 'result': expected_result}

    # Check the database
    statement = select(User).where(User.id == user.id)
    user = (await current_transaction.execute(statement)).unique().one()[0]

    assert user.name == data['name']
    assert user.surname == data['surname']
    assert user.country_id == data['country_id']


@pytest.mark.asyncio
async def test_post_user(app, test_client, current_transaction, setup_db):
    user = (
        await current_transaction.execute(
            select(User)
                .options(selectinload(User.roles))
                .where(User.id == DEFAULT_USER[0]['id'])
        )
    ).unique().one()[0]
    token = get_access_token(user)
    data = {
        'username': 'test2',
        'password': 'testpassword',
        'password_confirmation': 'testpassword',
        'name': 'Test2',
        'surname': 'User2',
        'email': 'test2@test.com',
        'country_id': 2,
        'role_ids': [1, 2]
    }

    response = await test_client.post(
        app.url_path_for('user.post_user'),
        headers={'Authorization': f'Bearer {token}'},
        data=data
    )

    # check the response
    assert response.status_code == 200

    json_response = response.json()
    user_id = json_response.get('result', {}).get('id')

    expected_result = {
        'id': user_id,
        'username': data['username'],
        'name': data['name'],
        'surname': data['surname'],
        'email': data['email'],
        'country': {
            'id': 2,
            'name': DEFAULT_COUNTRIES[1]['name'],
            'code': DEFAULT_COUNTRIES[1]['code']
        },
        'photo_url': None,
    }

    assert json_response == {'status': 200, 'message': None, 'result': expected_result}

    # Check the database
    statement = select(User).options(selectinload(User.roles)).where(User.id == user_id)
    user = (await current_transaction.execute(statement)).unique().one()[0]

    assert user.username == data['username']
    assert user.name == data['name']
    assert user.surname == data['surname']
    assert user.email == data['email']
    assert user.country_id == data['country_id']
    assert len(user.roles) == 2
