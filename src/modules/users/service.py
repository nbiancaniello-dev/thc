from collections.abc import Sequence
from datetime import timedelta
from core.config import settings
from core.exceptions import (
    DuplicateResourceError,
    ForbiddenError,
    InvalidCredentialsError,
    ResourceNotFoundError,
)
from core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from modules.users.models import User
from modules.users.repository import UserRepository
from modules.users.schemas import Token, UserCreate, UserUpdate

class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register_user(self, data: UserCreate) -> User:
        if await self.repository.get_by_username(data.username):
            raise DuplicateResourceError("Username already exists")

        if await self.repository.get_by_email(data.email):
            raise DuplicateResourceError("Email already exists")

        new_user = User(
            username=data.username,
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            dragon_ball_ids=data.dragon_ball_ids,
        )
        return await self.repository.create(new_user)

    async def authenticate(self, email: str, password: str) -> Token:
        user = await self.repository.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Incorrect email or password")

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
        )
        return Token(access_token=token, token_type="bearer")

    async def get_by_id(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User not found")
        return user

    async def get_all(self) -> Sequence[User]:
        users = await self.repository.get_all()
        if not users:
            raise ResourceNotFoundError("No users found")
        return users

    async def update_user(
        self,
        user_id: int,
        current_user_id: int,
        data: UserUpdate,
    ) -> User:
        if user_id != current_user_id:
            raise ForbiddenError("Not authorized to update this user")

        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User not found")

        if (
            data.username is not None
            and data.username.lower() != user.username.lower()
        ):
            if await self.repository.get_by_username(data.username):
                raise DuplicateResourceError("Username already exists")

        if (
            data.email is not None
            and data.email.lower() != user.email.lower()
        ):
            if await self.repository.get_by_email(data.email):
                raise DuplicateResourceError("Email already exists")

        update_dict = data.model_dump(exclude_unset=True)
        if "email" in update_dict and update_dict["email"] is not None:
            update_dict["email"] = update_dict["email"].lower()

        return await self.repository.update(user, update_dict)

    async def delete_user(self, user_id: int, current_user_id: int) -> None:
        if user_id != current_user_id:
            raise ForbiddenError("Not authorized to delete this user")

        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User not found")

        await self.repository.delete(user)

    async def get_by_id_with_dragon_ball(self, id: int) -> dict:
        result = await self.repository.find_by_id_with_dragon_ball(id)
        if not result:
            raise ResourceNotFoundError("User not found")
        return result

    async def get_all_with_dragon_balls(self) -> list[dict]:
        users = await self.repository.get_all_with_dragon_balls()
        if not users:
            raise ResourceNotFoundError("No users found")
        return users

    async def update_dragon_ball_ids(self, id: int, current_user_id: int, dragonBallIds: list[int]) -> User:
        if id != current_user_id:
            raise ForbiddenError("Not authorized to update this user's dragon ball IDs")

        user = await self.repository.get_by_id(id)
        if not user:
            raise ResourceNotFoundError(f"User with ID {id} not found")

        user.dragon_ball_ids = dragonBallIds
        return await self.repository.update(user, {"dragon_ball_ids": dragonBallIds})