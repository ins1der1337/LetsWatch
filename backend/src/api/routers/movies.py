from typing import Optional

from fastapi import APIRouter, Query

from api.dependencies import PaginationDep
from api.services.movies import search_model
from core.schemas.movies import MoviesResponseSchema

router = APIRouter(prefix="/movies", tags=["Фильмы"])


@router.get("", response_model=MoviesResponseSchema)
async def get_movies(
    pagination: PaginationDep,
    title: Optional[str] = Query(None, description="Поиск фильмов по названию"),
    genre: Optional[str] = Query(None, description="Поиск фильмов по жанру"),
    actor: Optional[str] = Query(None, description="Поиск фильмов по актеру"),
):
    """
    Запрос для получения фильма по:
    - Названию
    - Жанру
    - Актеру

    totalMovies: выводит количество всех найденных фильмов (изменять page можно до этого числа, иначе будет ошибка)
    """
    res = search_model.search_movies(pagination, title, genre, actor)
    return res
