from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from core.exceptions import (
    DuplicateResourceError,
    ForbiddenError,
    InvalidCredentialsError,
    ResourceNotFoundError,
)
from modules.users.dependencies import CurrentUser, get_user_service
from modules.users.schemas import (
    Token,
    UserCreate,
    UserDragonBallIdsUpdate,
    UserDragonBalls,
    UserPrivate,
    UserPublic,
    UserUpdate,
)
from modules.users.service import UserService

router = APIRouter()

@router.post(
    "",
    response_model=UserPrivate,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        return await service.register_user(user_data)
    except DuplicateResourceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        return await service.authenticate(
            email=form_data.username,
            password=form_data.password,
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.get("/me", response_model=UserPrivate)
async def get_current_user_profile(
    current_user: CurrentUser,
):
    return current_user


@router.get("", response_model=list[UserDragonBalls])
async def get_users(
    service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        return await service.get_all_with_dragon_balls()
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get("/{user_id}", response_model=UserDragonBalls)
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        return await service.get_by_id_with_dragon_ball(user_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch("/{user_id}", response_model=UserPrivate)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: CurrentUser,
    service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        return await service.update_user(
            user_id=user_id,
            current_user_id=current_user.id,
            data=user_data,
        )
    except ForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DuplicateResourceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        await service.delete_user(
            user_id=user_id,
            current_user_id=current_user.id,
        )
    except ForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch("/{user_id}/dragonball", response_model=UserPrivate)
async def update_dragon_ball_ids(
    user_id: int,
    update_dragon_ball_ids: UserDragonBallIdsUpdate,
    current_user: CurrentUser,
    service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        return await service.update_dragon_ball_ids(
            id=user_id,
            current_user_id=current_user.id,
            dragonBallIds=update_dragon_ball_ids.dragon_ball_ids,
        )
    except ForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc