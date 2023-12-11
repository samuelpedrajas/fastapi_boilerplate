from sqlmodel import Session
from sqlmodel import SQLModel, create_engine
from config import settings

engine = create_engine(settings.sqlalchemy_database_url)
metadata = SQLModel.metadata
sqlalchemy_database_url = settings.sqlalchemy_database_url

def get_db():
    with Session(engine) as session:
        yield session
