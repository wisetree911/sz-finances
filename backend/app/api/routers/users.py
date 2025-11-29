from fastapi import APIRouter, status, Depends
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.api.deps import get_user_service
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}",
             response_model=UserResponse,
             summary="Get detailed user info by user_id"
             )
async def get_user(user_id: int, service: UserService=Depends(get_user_service)):
    return await service.get_user_by_id(user_id=user_id)

@router.get("/", 
            response_model=list[UserResponse], 
            summary="Get all users detailed info"
            )
async def get_users(service: UserService=Depends(get_user_service)):
    return await service.get_all()

@router.post("/", 
             response_model=UserResponse, 
             summary="Create user"
             )
async def create_user(payload: UserCreate, service: UserService=Depends(get_user_service)):
    return await service.create_user(obj_in=payload)

@router.delete("/{user_id}", 
               status_code=status.HTTP_204_NO_CONTENT, 
               summary="Delete user by user_id"
               )
async def delete_user(user_id: int, service: UserService=Depends(get_user_service)):
    await service.delete_user(user_id=user_id)
    return
@router.patch("/{user_id}")
async def update(user_id: int, payload: UserUpdate, service: UserService=Depends(get_user_service)):
    return await service.update(user_id=user_id, payload=payload)
    
