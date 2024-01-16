from typing import Type, TypeVar, Generic, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select
from app.common.paginator import Paginator
from sqlalchemy.orm import joinedload
from sqlalchemy.inspection import inspect


T = TypeVar('T')


class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.model = model

    async def get_all(self, relationships_to_load: List[str] = None) -> List[T]:
        statement = select(self.model)
        statement = self._apply_relationships_loading(statement, relationships_to_load)
        results = await self.db.execute(statement)
        return results.all()

    async def get_by_field(self, field: str, value: Any, unique: bool = True, relationships_to_load: List[str] = None) -> List[T]:
        statement = select(self.model).where(getattr(self.model, field) == value)
        statement = self._apply_relationships_loading(statement, relationships_to_load)
        results = await self.db.execute(statement)
        if unique:
            return results.unique().all()
        return results.all()

    async def get_first_by_field(self, field: str, value: Any, unique: bool = True, relationships_to_load: List[str] = None) -> T:
        statement = select(self.model).where(getattr(self.model, field) == value)
        statement = self._apply_relationships_loading(statement, relationships_to_load)
        results = await self.db.execute(statement)
        if unique:
            results = results.unique()
        fetched_results = results.all()
        fetched_result = fetched_results[0] if fetched_results else None
        return fetched_result[0] if fetched_result else None

    # NOTE: not used but could be useful in the future
    # async def get_by_fields(self, fields: List[Tuple[str, Any]], use_or: bool = False, unique: bool = True) -> List[T]:
    #     if not fields:
    #         return []

    #     op = or_ if use_or else and_
    #     conditions = [getattr(self.model, field) == value for field, value in fields]
    #     statement = select(self.model).where(op(*conditions))
    #     results = await self.db.execute(statement)

    #     if unique:
    #         return results.unique().all()
    #     return results.all()

    async def create(self, obj: T) -> T:
        self.db.add(obj)
        return obj

    async def commit(self) -> None:
        await self.db.commit()

    async def flush(self) -> None:
        await self.db.flush()

    async def refresh(self, obj: T) -> T:
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: T) -> T:
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: T) -> None:
        await self.db.delete(obj)

    async def paginate(self, query: Select, page: int, per_page: int) -> dict:
        paginator = Paginator(self.db, query, page, per_page, self.model)
        return await paginator.get_response()

    async def ensure_relationships_loaded(self, instance: T, relationships: List[str]):
        for relationship in relationships:
            nested_relationships = relationship.split('.')
            current_instance = instance
            for rel_name in nested_relationships:
                if not rel_name not in inspect(instance).unloaded:
                    await self.db.refresh(
                        current_instance,
                        [rel_name],
                        with_for_update=False
                    )
                current_instance = getattr(current_instance, rel_name)

    def _apply_relationships_loading(self, statement: Select, relationships_to_load: List[str]):
        if relationships_to_load:
            for relationship_path in relationships_to_load:
                path_parts = relationship_path.split('.')
                load_option = None
                model = self.model

                for i, part in enumerate(path_parts):
                    if not hasattr(model, part):
                        raise AttributeError(f"Invalid relationship path: '{relationship_path}' at '{part}'")

                    prop = getattr(model, part)
                    mapper = inspect(model).relationships.get(part)

                    if not mapper:
                        raise AttributeError(f"No relationship found for '{part}' in '{model.__name__}'")

                    if i == 0:
                        load_option = joinedload(prop)
                    else:
                        load_option = load_option.joinedload(prop)

                    model = mapper.entity.class_


                if load_option:
                    statement = statement.options(load_option)
        return statement
