from typing import Type, TypeVar, Generic, List
from sqlmodel import SQLModel, Session, select

T = TypeVar('T', bound=SQLModel)

class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get_all(self) -> List[T]:
        statement = select(self.model)
        results = self.db.exec(statement)
        return results.all()

    def get_by_id(self, id: int) -> T:
        statement = select(self.model).where(self.model.id == id)
        results = self.db.exec(statement)
        return results.first()

    def delete_by_id(self, id: int) -> None:
        statement = select(self.model).where(self.model.id == id)
        self.db.delete(statement.first())
        self.db.commit()

    def create(self, object: T) -> T:
        self.db.add(object)
        self.db.commit()
        self.db.refresh(object)
        return object
