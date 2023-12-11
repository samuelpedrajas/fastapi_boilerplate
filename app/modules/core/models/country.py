from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from app.common.db import metadata


class Country(SQLModel, table=True, target_metadata=metadata):
    __tablename__ = "countries"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow,
                                 sa_column_kwargs={"onupdate": datetime.utcnow})
