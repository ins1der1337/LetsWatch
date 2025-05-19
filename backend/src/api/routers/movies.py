from fastapi import APIRouter

from api.dependencies import PaginationDep, FiltersDep
from api.services.movies import movie_db
from core.schemas.movies import MoviesResponseSchema

router = APIRouter(prefix="/movies", tags=["Фильмы"])


@router.get("", response_model=MoviesResponseSchema)
async def get_movies(pagination: PaginationDep, filters: FiltersDep):

    # TODO сделать запрос на количество фильмов в целом

    return MoviesResponseSchema(
        movies=[],
        filters=filters,
        pagination=pagination,
        total_pages=0,
        total_movies=0,
    )


@router.get("/{movie_id}")
async def get_movie_by_id(movie_id: int):
    pass


@router.get("/search-by-title/{title}")
async def get_movie_by_title(title: str, pagination: PaginationDep):
    res = movie_db.search_by_title(title, pagination)
    return res