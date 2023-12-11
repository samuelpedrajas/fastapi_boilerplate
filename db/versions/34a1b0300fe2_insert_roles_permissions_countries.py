"""insert basic data

Revision ID: 34a1b0300fe2
Revises: 7981ae0fe913
Create Date: 2023-11-22 13:20:33.831363

"""
from alembic import op
from db.utils import import_from_csv, insert_data_with_alembic


# revision identifiers, used by Alembic.
revision = '34a1b0300fe2'
down_revision = '077a1b7fc10b'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()

    import_from_csv(connection, 'countries', 'db/data/countries.csv')

    # Insert roles
    role_ids = insert_data_with_alembic(connection,
        [{'name': 'user'}, {'name': 'admin'}],
        table_name='roles')

    # Insert permissions
    permission_ids = insert_data_with_alembic(connection,
        [{'name': 'base'}, {'name': 'admin'}],
        table_name='permissions')

    # Insert roles_permissions
    insert_data_with_alembic(connection, [
        {'role_id': role_ids[0], 'permission_id': permission_ids[0]},
        {'role_id': role_ids[1], 'permission_id': permission_ids[0]},
        {'role_id': role_ids[1], 'permission_id': permission_ids[1]},
    ], table_name='roles_permissions')

def downgrade():
    op.execute('DELETE FROM users_roles')
    op.execute('DELETE FROM users')  # without countries, there are no users
    op.execute('DELETE FROM roles_permissions')
    op.execute('DELETE FROM countries')
    op.execute('DELETE FROM permissions')
    op.execute('DELETE FROM roles')
