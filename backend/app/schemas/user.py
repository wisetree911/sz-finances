from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.types import AwareDatetime


class APIModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra='forbid',
        str_strip_whitespace=True,
    )


class Role(str, Enum):
    admin = 'admin'
    user = 'user'


class UserFields(APIModel):
    name: str
    email: EmailStr
    role: Role = Field(default=Role.user)


class UserCreatePublic(UserFields):
    pass


class UserCreateAdm(UserFields):
    hashed_password: str | None = None


class UserUpdatePublic(UserFields):
    name: str | None = None
    email: EmailStr | None = None


class UserUpdateAdm(UserFields):
    name: str | None = None
    email: EmailStr | None = None
    hashed_password: str | None = None


class UserResponsePublic(UserFields):
    pass


class UserResponseAdm(UserFields):
    id: int
    hashed_password: str
    created_at: AwareDatetime


class UserRegister(APIModel):
    name: str
    email: EmailStr
    password: str
