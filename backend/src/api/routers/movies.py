from typing import Optional

from fastapi import APIRouter, Query

from api.dependencies import PaginationDep
from api.services.movies import search_model, recommend_model
from core.schemas.movies import MoviesResponseSchema

router = APIRouter(prefix="/movies", tags=["Фильмы"])


@router.get("", response_model=MoviesResponseSchema)
async def get_movies(
    pagination: PaginationDep,
    title: Optional[str] = Query(None, description="Поиск фильмов по названию"),
    genre: Optional[str] = Query(None, description="Поиск фильмов по жанру"),
    actor: Optional[str] = Query(None, description="Поиск фильмов по актеру"),
    director: Optional[str] = Query(None, description="Поиск фильмов по режиссеру"),
):
    """
    Запрос для получения фильма по:
    - Названию
    - Жанру
    - Актеру

    totalMovies: выводит количество всех найденных фильмов (изменять page можно до этого числа, иначе будет ошибка)
    """
    res = search_model.search_movies(pagination, title, genre, actor, director)
    return res


@router.get("/{title}/recommends", response_model=MoviesResponseSchema)
async def get_recommend_movies_for_title(
    pagination: PaginationDep,
    title: str,
):
    """
    Запрос для получения "похожих фильмов" по названию тайтла
    """
    res = recommend_model.recommend_movies_by_title(title, pagination)
    return res
