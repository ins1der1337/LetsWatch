from typing import Optional

from pydantic import BaseModel, Field
from fastapi import Query


class MovieReadSchema(BaseModel):
    id: int
    movie_id: int
    tmdb_id: int

    title: str = Field(max_length=64)
    description: str = Field(max_length=256)
    genres: list[str]
    year: int = Field(gt=0)
    poster_url: str
    director: str = Field(max_length=32)
    actors: str = Field(max_length=128)


class PaginationParams(BaseModel):
    limit: int = Field(5, gt=0, le=15)
    page: int = Field(1, ge=0)


class FiltersParams(BaseModel):
    title: Optional[str] = Field(None, max_length=64)
    genre: Optional[str] = Field(None, max_length=32)
    actor: Optional[str] = Field(None, max_length=32)


class MoviesResponseSchema(BaseModel):
    movies: list[MovieReadSchema]
    pagination: PaginationParams
    filters: Optional[FiltersParams] = None
    total_movies: int
    total_pages: int
