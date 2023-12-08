from sqlmodel import Session
from db.db import engine

def get_db():
    with Session(engine) as session:
        yield session
