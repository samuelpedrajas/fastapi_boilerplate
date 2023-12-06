import os
import unittest
from unittest import mock
from flask_testing import TestCase
from werkzeug.security import check_password_hash
from app import create_app, db
from app.models import User
from config import TestingConfig
from sqlalchemy.orm import scoped_session, sessionmaker
from app.models.email_template import EmailTemplate

class TestAuthViews(TestCase):
    def create_app(self):
        self.app = create_app(TestingConfig)
        return self.app

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.connection = db.engine.connect()
        self.transaction = self.connection.begin()
        self.session = scoped_session(sessionmaker(bind=self.connection))
        db.session = self.session

    def tearDown(self):
        db.session.remove()
        self.transaction.rollback()
        self.connection.close()

    # Test the register endpoint: success case
    @mock.patch('app.blueprints.auth.views.send_email')
    def test_register(self, send_email_mock):
        # Create a new user, multi-part form data is used to upload the photo
        with open('tests/integration/files/test_image.png', 'rb') as photo:
            data = {
                'username': 'testuser',
                'password': 'testpassword',
                'password_confirmation': 'testpassword',
                'name': 'Test',
                'surname': 'User',
                'email': 'test@test.com',
                'country_id': 1,
                'photo': (photo, 'test_image.png')
            }
            response = self.client.post(
                self.app.url_for('auth.register'),
                data=data,
                content_type='multipart/form-data'
            )

            # check the response
            user_id = None
            if response.json.get('result'):
                user_id = response.json['result'].get('user_id', None)

            self.assertDictEqual(
                response.json,
                {'status': 200, 'message': 'Registration successful', 'result': {'user_id': user_id}}
            )

            # check the database
            user = User.query.get(user_id)
            self.assertEqual(user.username, 'testuser')
            self.assertTrue(check_password_hash(user.password_hash, 'testpassword'))
            self.assertEqual(user.name, 'Test')
            self.assertEqual(user.surname, 'User')
            self.assertEqual(user.email, 'test@test.com')
            self.assertEqual(user.country_id, 1)
            self.assertEqual(user.photo_path, os.path.join(self.app.config['UPLOAD_FOLDER'], 'test_image.png'))
            self.assertFalse(user.active)
            self.assertEqual(len(user.roles), 1)
            self.assertEqual(user.roles[0].name, 'user')

            # check the email
            send_email_mock.assert_called_once()

            # activate the user
            confirmation_url = EmailTemplate.generate_confirmation_url(user)
            response = self.client.get(confirmation_url)
            self.assertEqual(response.status_code, 200)

            # reload the user
            user = User.query.get(user_id)
            self.assertTrue(user.active)

            # check we can't activate the user again
            response = self.client.get(confirmation_url)
            self.assertEqual(response.status_code, 400)

            # check we can't create a new user with the same username
            del data['photo']
            response = self.client.post(
                self.app.url_for('auth.register'),
                data=data,
                content_type='multipart/form-data'
            )
            self.assertEqual(response.status_code, 400)

    # Test the register endpoint: validation error case
    def test_register_validation_error(self):
        response = self.client.post(self.app.url_for('auth.register'), data={
            'username': '',
            'password': 'testpassword',
            'password_confirmation': 'testpassword2',
            'name': '',
            'surname': '',
            'email': '',
            'country_id': '',
            'photo_path': '',
        })

        # check the response
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json, {
            'status': 400,
            'message': 'Validation error',
            'result': {
                'username': ['This field is required.'],
                'password_confirmation': ['Password confirmation does not match.'],
                'name': ['This field is required.'],
                'surname': ['This field is required.'],
                'email': ['This field is required.'],
                'country_id': ['This field is required.']
            }
        })


if __name__ == '__main__':
    unittest.main()