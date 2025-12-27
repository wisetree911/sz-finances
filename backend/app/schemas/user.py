from pydantic import BaseModel, Field
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: str
    password: str


class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    name: str | None = None
    email: str | None = None
    password: str | None = None

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True