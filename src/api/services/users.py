from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions import NotFoundException, BadRequestException
from api.schemas.users import UserCreateSchema
from api.models import User


class UserRepository:

    @classmethod
    async def get_all_users(cls, session: AsyncSession) -> Iterable[User]:
        res = await session.execute(select(User))
        return res.scalars().all()

    @classmethod
    async def get_users_by_user_id(cls, session: AsyncSession, user_id: int) -> User:
        res = await session.scalar(select(User).filter(User.id == user_id))
        if not res:
            raise NotFoundException("Пользователь не найден")
        return res

    @classmethod
    async def create_user(
        cls, session: AsyncSession, user_data: UserCreateSchema
    ) -> User:
        existing_user = await session.scalar(
            select(User).where(User.username == user_data.username)
        )
        if existing_user:
            raise BadRequestException("Username already exists")

        session.add(new_user := User(**user_data.model_dump()))

        await session.commit()
        await session.refresh(new_user)

        return new_user

    @classmethod
    async def delete_user(cls, session: AsyncSession, user_id: int):
        pass

    @classmethod
    async def update_user(
        cls, session: AsyncSession, user_id: int, update_data: UserCreateSchema
    ) -> User:
        pass
