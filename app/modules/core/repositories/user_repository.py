from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.common.base_repository import BaseRepository
from app.modules.core.models.user import User

class UserRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_by_username(self, username: str) -> User:
        statement = select(self.model).where(self.model.username == username)
        results = await self.db.exec(statement)
        return results.first()
