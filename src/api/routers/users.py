from fastapi import APIRouter

from api.dependencies import DbSession, PaginationParams
from api.services.users import UserRepository
from core.schemas.users import UserCreateSchema, UserReadSchema, UserResponseSchema

router = APIRouter(tags=["Пользователи🤠"], prefix="/users")


# @router.get("", response_model=UserResponseSchema)
# async def get_users(
#     session: DbSession,
#     pagination: PaginationParams,
# ):
#     users = await UserRepository.get_all_users(session, pagination)
#
#     return UserResponseSchema(
#         users=[UserReadSchema.model_validate(user) for user in users],
#     )
#
#
# @router.get("/{tg_id}", response_model=UserReadSchema)
# async def get_user_by_user_id(session: DbSession, tg_id: int):
#     user = await UserRepository.get_user_by_tg_id(session, tg_id)
#     return user


@router.post("/{tg_id}", response_model=UserReadSchema)
async def create_user(
    tg_id: int,
    session: DbSession,
    data: UserCreateSchema,
):
    """
    Запрос на запись юзера в БД (по tg_id)
    Происходит при отправке `/start`
    """
    user = await UserRepository.create_user(session, tg_id, data)
    return user


@router.patch("/{tg_id}", response_model=UserReadSchema)
async def update_user(
    tg_id: int,
    session: DbSession,
    data: UserCreateSchema,
):
    """
    Обновление юзера в БД (по tg_id)
    Происходит при повторной отправке `/start` (если вдруг у пользователя поменялось имя)
    """
    new_user = await UserRepository.update_user(session, tg_id, data)
    return new_user
