from typing import Annotated

from app.api.dependencies import get_auth_service
from app.schemas.auth import RefreshToken, TokenPair
from app.schemas.user import UserRegister
from app.services.auth import AuthService
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    summary='Регистрация пользователя',
)
async def register(payload: UserRegister, service: AuthService = Depends(get_auth_service)):
    return await service.register(payload=payload)


@router.post(
    '/login',
    response_model=TokenPair,
    summary='Логин (получить access/refresh)',
    description='Принимает form-data: username, password (OAuth2PasswordRequestForm).',
)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(username=form.username, password=form.password)


@router.post(
    '/refresh',
    response_model=TokenPair,
    summary='Обновить токены по refresh',
)
async def refresh(payload: RefreshToken, service: AuthService = Depends(get_auth_service)):
    return await service.refresh(payload)


@router.post(
    '/logout',
    status_code=204,
    summary='Выйти (инвалидировать refresh)',
)
async def logout(payload: RefreshToken, service: AuthService = Depends(get_auth_service)):
    return await service.logout(payload=payload)
