from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    username: str


class UserReadSchema(BaseModel):
    id: int
    username: str
