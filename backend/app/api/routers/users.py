from fastapi import APIRouter, status
from app.schemas.user import UserCreate, UserResponse
from app.core.database import SessionDep

from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}",
             response_model=UserResponse,
             summary="Get detailed user info by user_id"
             )
async def get_user(session: SessionDep, user_id: int):
    return await UserService.get_by_user_id(session=session, user_id=user_id)

@router.get("/", 
            response_model=list[UserResponse], 
            summary="Get all users detailed info"
            )
async def get_users(session: SessionDep):
    return await UserService.get_all(session=session)

@router.post("/", 
             response_model=UserResponse, 
             summary="Create user"
             )
async def create_user(session: SessionDep, user_schema: UserCreate):
    return await UserService.create_user(session=session, user_schema=user_schema)

@router.delete("/{user_id}", 
               status_code=status.HTTP_204_NO_CONTENT, 
               summary="Delete user by user_id"
               )
async def delete_user(session: SessionDep, user_id: int):
    await UserService.delete_user(session=session, user_id=user_id)
    return
    
