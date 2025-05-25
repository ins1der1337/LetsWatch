from typing import Optional

from pydantic import BaseModel, Field


class MovieReadSchema(BaseModel):
    movie_id: int
    title: str = Field(max_length=256)
    genres: Optional[list[str]]
    description: Optional[str] = Field(max_length=2048)
    year: int = Field(gt=0)
    poster_url: str
    rating: float = Field(..., ge=0, le=10)
    rating_counts: int

    director: Optional[str] = Field(max_length=64)
    actors: Optional[list[str]]


class PaginationParams(BaseModel):
    limit: int = Field(5, gt=0, le=15)
    page: int = Field(1, gt=0, le=10)


class FiltersParams(BaseModel):
    title: Optional[str] = Field(None, max_length=64)
    genre: Optional[str] = Field(None, max_length=32)
    actor: Optional[str] = Field(None, max_length=32)


class MoviesResponseSchema(BaseModel):
    movies: list[MovieReadSchema]
    pagination: PaginationParams
    totalMovies: int
