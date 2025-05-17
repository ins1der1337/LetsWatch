from pydantic import BaseModel, Field


class MoviesReadSchema(BaseModel):
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


class MoviesResponseSchema(BaseModel):
    movies: MoviesReadSchema
    total_movies: int


class PaginationSchema(BaseModel):
    limit: int = Field(5, gt=0, le=15)
    page: int = Field(1, ge=0)
