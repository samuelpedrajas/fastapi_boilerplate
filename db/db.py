from sqlalchemy import MetaData, create_engine
from app.common.db import sqlalchemy_database_url, Base
from config import settings

sqlalchemy_database_url = settings.sqlalchemy_database_url
engine = create_engine(sqlalchemy_database_url.replace('+asyncpg', ''))
metadata = MetaData()
