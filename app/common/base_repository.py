from typing import Type, TypeVar, Generic, List
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar('T', bound=SQLModel)

class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.model = model

    async def get_all(self) -> List[T]:
        statement = select(self.model)
        results = await self.db.exec(statement)
        return results.all()

    async def get_by_id(self, id: int) -> T:
        statement = select(self.model).where(self.model.id == id)
        results = await self.db.exec(statement)
        return results.first()

    async def delete_by_id(self, id: int) -> None:
        statement = select(self.model).where(self.model.id == id)
        obj = await self.db.get(statement)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()

    async def create(self, object: T) -> T:
        self.db.add(object)
        await self.db.commit()
        await self.db.refresh(object)
        return object

    async def update(self, object: T) -> T:
        await self.db.commit()
        await self.db.refresh(object)
        return object
