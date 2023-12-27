from typing import Type, TypeVar, Generic, List
from sqlmodel import SQLModel, select, Column
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

    async def get_by_field(self, field: Column, value: str) -> T:
        statement = select(self.model).where(field == value)
        results = await self.db.exec(statement)
        return results.first()

    async def create(self, obj: T) -> T:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: T) -> T:
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: T) -> None:
        await self.db.delete(obj)
        await self.db.commit()

