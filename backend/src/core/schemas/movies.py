from typing import Optional

from pydantic import BaseModel, Field
from fastapi import Query


class MovieReadSchema(BaseModel):
    movieId: int
    title: str = Field(max_length=64)
    genres: list[str]
    description: str = Field(None, max_length=827)
    year: int = Field(gt=0)
    poster_url: str
    director: str = Field(max_length=32)
    actors: list[str]


class PaginationParams(BaseModel):
    limit: int = Field(1, gt=0, le=15)
    page: int = Field(1, gt=0, le=10)


class FiltersParams(BaseModel):
    title: Optional[str] = Field(None, max_length=64)
    genre: Optional[str] = Field(None, max_length=32)
    actor: Optional[str] = Field(None, max_length=32)


class MoviesResponseSchema(BaseModel):
    movies: list[MovieReadSchema]
    pagination: PaginationParams
    totalMovies: int
