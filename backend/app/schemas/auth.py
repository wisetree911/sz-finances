from pydantic import BaseModel, ConfigDict
from pydantic.types import AwareDatetime


class APIModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra='forbid',
        str_strip_whitespace=True,
    )


class TokenPair(APIModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RefreshToken(APIModel):
    refresh_token: str


class RefreshSessionCreate(APIModel):
    user_id: int
    jti: str
    token_hash: str
    expires_at: AwareDatetime
