from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    tg_id: int
    username: str


class UserReadSchema(UserCreateSchema):
    id: int
