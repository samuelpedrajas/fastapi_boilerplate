from typing import Type, TypeVar, Generic, List
from sqlmodel import SQLModel, Session

T = TypeVar('T', bound=SQLModel)

class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get_all(self) -> List[T]:
        return self.db.exec(self.model).all()

    def get_by_id(self, id: int) -> T:
        return self.db.exec(self.model).filter(self.model.id == id).first()

    def delete_by_id(self, id: int) -> None:
        self.db.exec(self.model).filter(self.model.id == id).delete()
        self.db.commit()

    def create(self, object: Type[T]) -> Type[T]:
        self.db.add(object)
        self.db.commit()

        return object
