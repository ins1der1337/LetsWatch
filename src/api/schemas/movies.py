from datetime import datetime

from pydantic import BaseModel, Field


class MoviesReadSchema(BaseModel):
    id: int

    title: str = Field(max_length=64)
    description: str = Field(max_length=128)
    genres: list[str]
    year: int = Field(gt=0)
    poster_url: str
    director: str = Field(max_length=32)
    actors: str = Field(max_length=128)

    created_at: datetime
    updated_at: datetime
