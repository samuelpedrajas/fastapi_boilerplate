import csv
from datetime import datetime
from sqlalchemy import Table
from sqlalchemy.sql import insert
from env import metadata


def get_table(connection, table_name):
    table = Table(table_name, metadata, autoload_with=connection)
    return table


def insert_data_with_alembic(connection, batch_data, table_name=None, table=None):
    if table_name is None and table is None:
        raise ValueError('Either table_name or table must be provided')
    if table is None:
        table = get_table(connection, table_name)

    # Check if the table has 'created_at' and/or 'updated_at' columns
    now = datetime.now()
    if 'created_at' in table.c:
        for row in batch_data:
            row['created_at'] = row.get('created_at', now)
    if 'updated_at' in table.c:
        for row in batch_data:
            row['updated_at'] = row.get('updated_at', now)

    stmt = insert(table).values(batch_data)
    stmt = stmt.returning(table.c.id)
    result = connection.execute(stmt)
    return [row[0] for row in result.fetchall()]


def import_from_csv(connection, table_name, csv_file_path, delimiter=',', batch_size=1000):
    table = get_table(connection, table_name)

    batch_data = []
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        for row in reader:
            batch_data.append(row)
            if len(batch_data) >= batch_size:
                insert_data_with_alembic(connection, batch_data, table=table)
                batch_data = []
        # Insert any remaining rows in the last batch
        if batch_data:
            insert_data_with_alembic(connection, batch_data, table=table)
