from requests import session
from shared.repositories.user import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session=session)

    async def get_all(self):
        return await self.repo.get_all()
    
    async def get_user_by_id(self, user_id: int):
        user = await self.repo.get_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(404, "SZ user not found")
        return user

    async def create_user(self, user_schema):
        return await self.repo.create(
            name=user_schema.name,
            age=user_schema.age
            )

    async def delete_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(404, "SZ user not found")
        await self.repo.delete(user=user)