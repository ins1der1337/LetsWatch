from fastapi import APIRouter

from api.dependencies import PaginationParams

router = APIRouter(prefix="/movies", tags=["Фильмы"])


@router.get("")
async def get_movies(pagination: PaginationParams):
    pass


@router.get("/{movie_id}")
async def get_movie_by_id(movie_id: int):
    pass
