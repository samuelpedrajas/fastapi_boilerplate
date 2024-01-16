from pydantic import AnyHttpUrl, Field, BaseModel
from typing import Optional, Generic, Type, TypeVar, List
from sqlalchemy import Select, distinct, func, select
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.middlewares import request_object


M = TypeVar('M')


class Paginator:
    def __init__(self, db: AsyncSession, query: Select, page: int, per_page: int, primary_entity: Type[BaseModel]):
        self.db = db
        self.query = query
        self.page = page
        self.per_page = per_page
        self.limit = per_page * page
        self.offset = (page - 1) * per_page
        self.request = request_object.get()
        self.number_of_pages = 0
        self.next_page = ''
        self.previous_page = ''
        self.primary_entity = primary_entity

    def _get_next_page(self) -> Optional[str]:
        if self.page >= self.number_of_pages:
            return
        url = self.request.url.include_query_params(page=self.page + 1)
        return str(url)

    def _get_previous_page(self) -> Optional[str]:
        if self.page == 1 or self.page > self.number_of_pages + 1:
            return
        url = self.request.url.include_query_params(page=self.page - 1)
        return str(url)

    async def get_response(self) -> dict:
        return {
            'count': await self._get_total_count(),
            'number_of_pages': self.number_of_pages,
            'next_page': self._get_next_page(),
            'previous_page': self._get_previous_page(),
            'items': [todo for todo in (await self.db.scalars(self.query.limit(self.limit).offset(self.offset))).unique()]
        }

    def _get_number_of_pages(self, count: int) -> int:
        rest = count % self.per_page
        quotient = count // self.per_page
        return quotient if not rest else quotient + 1


    async def _get_total_count(self) -> int:
        primary_key = self.primary_entity.__table__.primary_key.columns.values()[0]
        subquery = self.query.subquery()
        count_query = select(func.count(distinct(subquery.c[primary_key.name])))
        count = await self.db.scalar(count_query)
        self.number_of_pages = self._get_number_of_pages(count)
        return count

class PaginatedResponse(BaseModel, Generic[M]):
    count: int = Field(description='Number of total items')
    items: List[M] = Field(description='List of items returned in a paginated response')
    next_page: Optional[AnyHttpUrl] = Field(None, description='url of the next page if it exists')
    previous_page: Optional[AnyHttpUrl] = Field(None, description='url of the previous page if it exists')
