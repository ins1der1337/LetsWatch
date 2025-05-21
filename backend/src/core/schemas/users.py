from datetime import datetime

from pydantic import BaseModel, ConfigDict

from core.schemas.movies import PaginationParams


class UserCreateSchema(BaseModel):
    username: str

    model_config = ConfigDict(extra="forbid")


class UserReadSchema(UserCreateSchema):
    id: int
    tg_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponseSchema(BaseModel):
    users: list[UserReadSchema]
    pagination: PaginationParams
