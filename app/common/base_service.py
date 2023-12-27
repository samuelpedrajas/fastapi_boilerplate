from typing import TypeVar, List, Any
from sqlmodel import SQLModel, select, Column
from app.common.base_repository import BaseRepository


T = TypeVar('T', bound=SQLModel)

class BaseService:
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    async def get_all(self) -> List[T]:
        return await self.repository.get_all()

    async def get_by_field(self, field: Column, value: Any) -> List[T]:
        return await self.repository.get_by_field(field, value)

    async def get_first_by_field(self, field: Column, value: Any) -> T:
        return await self.repository.get_first_by_field(field, value)

    async def update(self, obj: T) -> T:
        return await self.repository.update(obj)

    async def delete(self, obj: T) -> None:
        return await self.repository.delete(obj)
