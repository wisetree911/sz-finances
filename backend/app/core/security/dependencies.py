from app.api.dependencies import get_user_service
from app.core.config import settings
from app.services.users import UserService
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: UserService = Depends(get_user_service),  # noqa: B008
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        if payload.get('type') != 'access':  # чтобы точно на рефреше не получили ничего
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token type'
            )

        user_id = payload.get('sub')
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    except JWTError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from err

    user = await service.get_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
