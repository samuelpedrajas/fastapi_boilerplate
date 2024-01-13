import os
import pytest
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import select
from config import settings
from unittest import mock
from app.helpers.security import encrypt
from app.modules.core.models.user import User
from tests.conftest import app, test_client, current_transaction


@pytest.mark.asyncio
async def test_register(app, test_client, current_transaction):
    with mock.patch('app.modules.core.services.email_service.EmailService.send_email') as mock_send_email:
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'password_confirmation': 'testpassword',
            'name': 'Test',
            'surname': 'User',
            'email': 'test@test.com',
            'country_id': '1'
        }
        with open('tests/integration/files/test_image.png', 'rb') as photo:
            files = {
                'photo': (photo.name, photo, 'image/png')  # Provide the file's name and content type
            }

            response = await test_client.post(app.url_path_for('auth.register'), data=data, files=files)

        # check the response
        assert response.status_code == 200

        json_response = response.json()
        user_id = json_response.get('result', {}).get('id')

        expected_result = {
            'country': {
                'code': 'C1', 'id': 1, 'name': 'Country1'
            },
            'email': data['email'],
            'id': 1,
            'name': data['name'],
            'surname': data['surname'],
            'username': data['username'],
        }
        assert response.json() == {'status': 200, 'message': 'Registration successful', 'result': expected_result}

        # Check the database
        statement = select(User).options(selectinload(User.roles)).where(User.id == user_id)
        user = (await current_transaction.exec(statement)).unique().one()
        assert user.username == 'testuser'
        assert user.name == 'Test'
        assert user.surname == 'User'
        assert user.email == 'test@test.com'
        assert user.country_id == 1
        assert user.photo_path.startswith(settings.UPLOADS_DIR)
        assert os.path.isfile(user.photo_path)
        assert not user.active
        assert len(user.roles) == 1
        assert user.roles[0].name == 'user'

        # check the email
        mock_send_email.assert_called_once()

        # activate the user
        token = encrypt(user_id)
        confirmation_url = app.url_path_for('auth.confirm') + f'?token={token}'
        response = await test_client.get(confirmation_url)
        assert response.status_code == 200

        # reload the user
        statement = select(User).where(User.id == user_id)
        user = (await current_transaction.exec(statement)).unique().one()
        assert user.active

        # check we can't activate the user again
        response = await test_client.get(confirmation_url)
        assert response.status_code == 400

        # check we can't create a new user with the same username
        response = await test_client.post(app.url_path_for('auth.register'), data=data)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_validation_error(app, test_client, current_transaction):
    response = await test_client.post(app.url_path_for('auth.register'), data={
        'username': '',
        'password': 'testpassword',
        'password_confirmation': 'testpassword2',
        'name': '',
        'surname': '',
        'email': '',
        'country_id': '1',
        'photo': '',
    })

    # check the database
    count_query = select(func.count()).select_from(User)
    user_count = (await current_transaction.exec(count_query)).first()

    assert user_count == 0

    # check the response
    assert response.status_code == 422
    assert response.json() == {
        'status': 422,
        'message': 'Validation Error',
        'result': {
            'detail': [
                {
                    'type': 'missing',
                    'loc': ['body', 'username'],
                    'msg': 'Field required',
                    'input': None,
                    'url': 'https://errors.pydantic.dev/2.5/v/missing'
                },
                {
                    'type': 'missing',
                    'loc': ['body', 'name'],
                    'msg': 'Field required',
                    'input': None,
                    'url': 'https://errors.pydantic.dev/2.5/v/missing'
                },
                {
                    'type': 'missing',
                    'loc': ['body', 'surname'],
                    'msg': 'Field required',
                    'input': None,
                    'url': 'https://errors.pydantic.dev/2.5/v/missing'
                },
                {
                    'type': 'missing',
                    'loc': ['body', 'email'],
                    'msg': 'Field required',
                    'input': None,
                    'url': 'https://errors.pydantic.dev/2.5/v/missing'
                },
            ]
        }
    }