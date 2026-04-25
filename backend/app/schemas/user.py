from app.schemas.common.enums import Role
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class APIModel(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
        from_attributes=True,
        str_strip_whitespace=True,
    )


class UserFields(APIModel):
    name: str
    email: EmailStr
    role: Role = Field(...)


class UserCreate(UserFields):
    hashed_password: str | None = None


class UserUpdate(APIModel):
    name: str | None = None
    email: EmailStr | None = None
    role: Role | None = None


class UserResponse(UserFields):
    id: int


class UserRegister(APIModel):
    name: str
    email: EmailStr
    password: str
    role: str  # tmp
