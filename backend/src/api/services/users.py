from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions import NotFoundException, BadRequestException
from core.schemas.movies import PaginationParams
from core.schemas.users import UserCreateSchema
from core.models import User


class UserRepository:

    @classmethod
    async def create_user(
        cls, session: AsyncSession, tg_id: int, user_data: UserCreateSchema
    ) -> User:
        existing_user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if existing_user:
            raise BadRequestException("Такой пользователь уже зарегистрирован")

        data = {"tg_id": tg_id, **user_data.model_dump()}

        session.add(new_user := User(**data))

        await session.commit()
        await session.refresh(new_user)

        return new_user

    @classmethod
    async def update_user(
        cls, session: AsyncSession, tg_id: int, user_update_data: UserCreateSchema
    ) -> User:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            raise NotFoundException("Такого пользователя нет")

        for key, value in user_update_data:
            if not hasattr(user, key):
                raise BadRequestException(f"Такого столбца у пользователя нет: {key}")
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)

        return user

    @classmethod
    async def get_all_users(
        cls, session: AsyncSession, pagination: PaginationParams
    ) -> Sequence[User]:
        query = (
            select(User)
            .offset((pagination.page - 1) * pagination.limit)
            .limit(pagination.limit)
        )
        res = await session.execute(query)
        return res.scalars().all()

    @classmethod
    async def get_user_by_tg_id(
        cls, session: AsyncSession, tg_id: int, not_found_error: bool = True
    ) -> User:
        res = await session.scalar(select(User).filter(User.tg_id == tg_id))
        if not res and not_found_error:
            raise NotFoundException("Пользователь не найден")
        return res
