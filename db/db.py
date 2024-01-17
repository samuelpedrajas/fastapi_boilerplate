from sqlalchemy import MetaData, create_engine
from app.common.db import sqlalchemy_database_url, Base
from config import settings


engine = create_engine(settings.sqlalchemy_database_url.replace('+asyncpg', ''))
metadata = MetaData()
