from sqlalchemy import select
from shared.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int):
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        return user
    
    async def get_all(self):
        query = select(User)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create(self, name: str, age: int):
        new_user = User(
            name=name, 
            age=age
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user) # достать + айдишник от бд
        return new_user
    
    async def delete(self, user: User):
        await self.session.delete(user)
        await self.session.commit()
    
    
