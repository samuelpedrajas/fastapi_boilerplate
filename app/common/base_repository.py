from typing import Type, TypeVar, Generic, List, Tuple, Any
from sqlmodel import SQLModel, select, and_, or_
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

    async def get_by_field(self, field: str, value: Any, unique: bool = True) -> List[T]:
        statement = select(self.model).where(getattr(self.model, field) == value)
        results = await self.db.exec(statement)
        if unique:
            return results.unique().all()
        return results.all()

    async def get_first_by_field(self, field: str, value: Any, unique: bool = True) -> T:
        results = await self.get_by_field(field, value, unique)
        if results:
            return results[0]
        return None

    async def get_by_fields(self, fields: List[Tuple[str, Any]], use_or: bool = False, unique: bool = True) -> List[T]:
        if not fields:
            return []

        op = or_ if use_or else and_
        conditions = [getattr(self.model, field) == value for field, value in fields]
        statement = select(self.model).where(op(*conditions))
        results = await self.db.exec(statement)

        if unique:
            return results.unique().all()
        return results.all()

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

