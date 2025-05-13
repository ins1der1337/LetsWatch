from fastapi import APIRouter

from api.schemas.users import UserCreateSchema, UserReadSchema
from api.services.users import UserRepository
from database.core import DbSession

router = APIRouter(tags=["Пользователи🤠"], prefix="/users")


@router.get("", response_model=list[UserReadSchema])
async def get_users(session: DbSession):
    users = await UserRepository.get_all_users(session)
    return users


@router.get("/{user_id}", response_model=UserReadSchema)
async def get_user_by_user_id(session: DbSession, user_id: int):
    user = await UserRepository.get_users_by_user_id(session, user_id)
    return user


@router.post("", response_model=UserReadSchema)
async def create_user(session: DbSession, data: UserCreateSchema):
    user = await UserRepository.create_user(session, data)
    return user


@router.put("/{user_id}")
async def update_user(session: DbSession, user_id: int, update_data: UserCreateSchema):
    pass


@router.delete("/{user_id}")
async def delete_user(session: DbSession, user_id: int):
    pass
