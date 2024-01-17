"""insert email templates

Revision ID: 03f38e636f9f
Revises: 34a1b0300fe2
Create Date: 2023-11-23 11:07:18.487387

"""
from alembic import op
from db.utils import insert_data_with_alembic


# revision identifiers, used by Alembic.
revision = '03f38e636f9f'
down_revision = '34a1b0300fe2'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()

    # Insert email templates
    email_templates = [
        {
            'name': 'account_confirmation',
            'subject': 'Please, confirm your email address',
            'html_body': '<p>Hi @@name@@,</p><p>Click <a href="@@confirmation_url@@">here</a> to confirm your email address.</p>',
        },
        {
            'name': 'password_reset',
            'subject': 'Reset your password',
            'html_body': '<p>Hi @@name@@,</p><p>Click <a href="@@password_reset_url@@">here</a> to reset your password.</p>',
        }
    ]
    templates = insert_data_with_alembic(connection, email_templates, 'email_templates')

    # Insert email variables
    email_variables = [
        {'variable': 'name', 'description': 'The name of the user'},
        {'variable': 'surname', 'description': 'The surname of the user'},
        {'variable': 'confirmation_url', 'description': 'The URL to confirm the user email address'},
        {'variable': 'password_reset_url', 'description': 'The URL to reset the user password'},
    ]
    variables = insert_data_with_alembic(connection, email_variables, 'email_variables')

    insert_data_with_alembic(connection, [
        {'email_template_id': templates[0], 'email_variable_id': variables[0]},
        {'email_template_id': templates[0], 'email_variable_id': variables[1]},
        {'email_template_id': templates[0], 'email_variable_id': variables[2]},
        {'email_template_id': templates[1], 'email_variable_id': variables[0]},
        {'email_template_id': templates[1], 'email_variable_id': variables[1]},
        {'email_template_id': templates[1], 'email_variable_id': variables[3]},
    ], table_name='email_templates_email_variables')


def downgrade():
    op.execute('DELETE FROM email_templates_email_variables')
    op.execute('DELETE FROM email_templates')
    op.execute('DELETE FROM email_variables')
