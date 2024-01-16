from typing import TypeVar, List, Any
from sqlalchemy import Column
from app.common.base_repository import BaseRepository


T = TypeVar('T')

class BaseService:
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    async def get_all(self, relationships_to_load: List[str] = None) -> List[T]:
        return await self.repository.get_all(relationships_to_load)

    async def get_by_field(self, field: Column, value: Any,  unique=True, relationships_to_load: List[str] = None) -> List[T]:
        return await self.repository.get_by_field(field, value, unique, relationships_to_load)

    async def get_first_by_field(self, field: Column, value: Any,  unique=True, relationships_to_load: List[str] = None) -> T:
        return await self.repository.get_first_by_field(field, value, unique, relationships_to_load)

    async def delete(self, obj: T) -> None:
        return await self.repository.delete(obj)
