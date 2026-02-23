from app.schemas.common.enums import Role
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.types import AwareDatetime


class APIModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra='forbid',
        str_strip_whitespace=True,
    )


class UserFields(APIModel):
    name: str
    email: EmailStr
    role: Role = Field(default=Role.user)


class UserCreate(UserFields):
    hashed_password: str | None = None


class UserUpdate(UserFields):
    name: str | None = None
    email: EmailStr | None = None


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
    role: str  # tmp
