from fastapi import APIRouter

from api.dependencies import PaginationDep
from api.services.movies import movie_db
from core.schemas.movies import MoviesResponseSchema

router = APIRouter(prefix="/movies", tags=["Фильмы"])


@router.get("/search-by-title/{title}", response_model=MoviesResponseSchema)
async def get_movie_by_title(title: str, pagination: PaginationDep):
    """
    Запрос для получения фильма по названию + похожие

    totalMovies: выводит количество всех найденных фильмов (изменять page можно до этого числа, иначе будет ошибка)
    """
    res = movie_db.search_by_title(title, pagination)
    return res


@router.get("/search-by-genre/{genre}", response_model=MoviesResponseSchema)
async def get_movie_by_title(genre: str, pagination: PaginationDep):
    """
    Запрос для получения фильмов по жанру

    totalMovies: выводит количество всех найденных фильмов (изменять page можно до этого числа, иначе будет ошибка)
    """
    res = movie_db.search_by_genre(genre, pagination)
    return res


@router.get("/search-by-actor/{actor}", response_model=MoviesResponseSchema)
async def get_movie_by_actor(actor: str, pagination: PaginationDep):
    """
    Запрос для получения фильмов по актеру

    totalMovies: выводит количество всех найденных фильмов (изменять page можно до этого числа, иначе будет ошибка)
    """
    res = movie_db.search_by_actor(actor, pagination)
    return res
