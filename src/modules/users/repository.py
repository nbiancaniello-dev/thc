from collections.abc import Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from modules.users.models import User
from clients.dragon_ball_client import DragonBallClient

class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.dragon_ball_client = DragonBallClient()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(User).where(func.lower(User.username) == username.lower())
        )
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(func.lower(User.email) == email.lower())
        )
        return result.scalars().first()

    async def get_all(self) -> Sequence[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User, update_data: dict) -> User:
        for field, value in update_data.items():
            setattr(user, field, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def update_dragon_ball_ids(self, id: int, dragon_ball_ids: list[int]) -> User | None:
        await self.update(await self.get_by_id(id), { "dragon_ball_ids": dragon_ball_ids })
        return await self.get_by_id(id)

    async def add_dragon_ball_to_user(self, user_id: int, dragon_ball_id: int) -> User | None:
        user = await self.get_by_id(user_id)

        if not user:
            return None

        current_ids = list(user.dragon_ball_ids or [])
        if dragon_ball_id not in current_ids:
            await self.update(user, { "dragon_ball_ids": [*current_ids, dragon_ball_id] })

        return user

    async def remove_dragon_ball_from_user(self, user_id: int, dragon_ball_id: int) -> User | None:
        user = await self.get_by_id(user_id)

        if not user:
            return None

        remaining_ids = [id for id in (user.dragon_ball_ids or []) if id != dragon_ball_id]
        await self.update(user, { "dragon_ball_ids": remaining_ids })

        return user

    async def find_by_id_with_dragon_ball(self, id: int) -> dict | None:
        user = await self.get_by_id(id)

        if not user:
            return None

        # Fetch the character names for the stored dragon_ball_ids
        characters = await self.dragon_ball_client.get_dragon_ball_characters_by_ids(
            user.dragon_ball_ids,
        )
        return self._with_dragon_balls(user, {c["id"]: c for c in characters})

    async def get_all_with_dragon_balls(self) -> list[dict]:
        users = await self.get_all()

        # Fetch every distinct id once, instead of once per user
        all_ids = [id for user in users for id in (user.dragon_ball_ids or [])]
        characters = await self.dragon_ball_client.get_dragon_ball_characters_by_ids(all_ids)
        characters_by_id = {c["id"]: c for c in characters}

        return [self._with_dragon_balls(user, characters_by_id) for user in users]

    @staticmethod
    def _with_dragon_balls(user: User, characters_by_id: dict[int, dict]) -> dict:
        ids = user.dragon_ball_ids or []
        return {
            "id": user.id,
            "username": user.username,
            "dragon_ball_ids": user.dragon_ball_ids,
            "dragon_balls": [characters_by_id[id] for id in ids if id in characters_by_id],
        }
