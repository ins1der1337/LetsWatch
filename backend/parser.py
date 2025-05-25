import asyncio
from typing import Optional

import aiohttp
import pandas as pd
from aiohttp import ClientSession
from pandas import DataFrame
from pydantic import BaseModel, Field

from core.config import settings

BASE_URL = "https://api.themoviedb.org/3/movie"
API_KEY = settings.tmdb.api_key


class MovieDataRead(BaseModel):
    tmdb_id: int
    title: str = Field(max_length=128)
    description: Optional[str] = Field(max_length=2048)
    year: Optional[int] = Field(gt=0)
    poster_url: Optional[str]
    genres: Optional[list[str]]
    actors: Optional[list[str]]
    director: Optional[str]
    rating: Optional[float] = Field(ge=0, le=10)
    rating_counts: Optional[int]


def form_movie_data(
    tmdb_id: int, movie_data: dict, credits_data: dict
) -> MovieDataRead:
    poster_path: Optional[str] = movie_data.get("poster_path", None)
    poster_url: Optional[str] = (
        f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
    )

    cast: list[dict] = sorted(
        credits_data.get("cast", []),
        key=lambda person: person["popularity"],
        reverse=True,
    )
    actors: Optional[list[str]] = [man["name"] for man in cast][:5] if cast else None

    crew: list[dict] = credits_data.get("crew", [])
    director: Optional[str] = crew[0]["name"] if crew else None

    release_date: Optional[str] = movie_data.get("release_date", None)
    year: Optional[int] = int(release_date.split("-")[0]) if release_date else None

    movie = {
        "tmdb_id": tmdb_id,
        "title": movie_data.get("title", ""),
        "description": ".".join(movie_data.get("overview", "").split(".")[:2]),
        "poster_url": poster_url,
        "year": year,
        "genres": [
            str(genre["name"]).capitalize() for genre in movie_data.get("genres", [])
        ][:5],
        "rating": movie_data.get("vote_average", None),
        "rating_counts": movie_data.get("vote_count", None),
        "actors": actors,
        "director": director,
    }

    return MovieDataRead.model_validate(movie)


async def fetch_movie_data(
    session: ClientSession, tmdb_id: int
) -> Optional[MovieDataRead]:
    try:
        movie_url = f"{BASE_URL}/{int(tmdb_id)}?language=ru"
        credits_url = f"{BASE_URL}/{int(tmdb_id)}/credits?language=ru"

        headers = {"accept": "application/json", "Authorization": f"Bearer {API_KEY}"}

        async with session.get(movie_url, headers=headers) as movie_resp:
            movie_data = await movie_resp.json()

        async with session.get(credits_url, headers=headers) as credits_resp:
            credits_data = await credits_resp.json()

        movie = form_movie_data(tmdb_id, movie_data, credits_data)
        print(f"{tmdb_id}. Фильм '{movie.title}' успешно прошел валидацию")
        return movie

    except Exception as e:
        print(f"Ошибка при запросе фильма {tmdb_id}: {e}")
        return None


# # Функция запроса данных по одному tmdb_id
# async def fetch_movie_data(session, tmdb_id: int):
#     try:
#         # Запрос основной информации
#         movie_url = f"{BASE_URL}/{tmdb_id}?api_key={API_KEY}&language=ru"
#         credits_url = f"{BASE_URL}/{tmdb_id}/credits?api_key={API_KEY}&language=ru"
#
#         async with session.get(movie_url) as movie_resp:
#             movie_data = await movie_resp.json()
#
#         description: Optional[str] = movie_data.get("overview", None)
#
#         poster_path: Optional[str] = movie_data.get("poster_path", None)
#         poster_url: Optional[str] = (
#             f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
#         )
#
#         genres: list[Optional[str]] = [
#             str(genre["name"]).capitalize() for genre in movie_data.get("genres", [])
#         ]
#
#         rating: Optional[float] = movie_data.get("vote_average", None)
#         rating_counts: Optional[int] = movie_data.get("vote_count", None)
#
#         async with session.get(credits_url) as credits_resp:
#             credits_data = await credits_resp.json()
#
#         actors: list[Optional[str]] = [
#             str(a["name"]) for a in credits_data.get("cast", [])[:5]
#         ]
#
#         director: Optional[str] = next(
#             (p["name"] for p in credits_data.get("crew", []) if p["job"] == "Director"),
#             None,
#         )
#
#         print(f"Обработан tmdb_id: {tmdb_id}")
#
#         return {
#             "tmdb_id": tmdb_id,
#             "description": description.capitalize(),
#             "genres": genres,
#             "actors": actors,
#             "rating": rating,
#             "rating_counts": rating_counts,
#             "director": director.capitalize(),
#             "poster_url": poster_url,
#         }
#
# except Exception as e:
#     print(f"Ошибка при обработке tmdb_id {tmdb_id}: {e}")
#     return {
#         "tmdbId": tmdb_id,
#         "description": None,
#         "poster_url": None,
#         "director": None,
#         "actors": None,
#     }


# Основной цикл с лимитом 40 запросов/сек
async def fetch_all(df: DataFrame):
    results = []
    connector = aiohttp.TCPConnector(limit=40)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i, tmdb_id in enumerate(df["tmdbId"]):

            tasks.append(fetch_movie_data(session, tmdb_id))

            # Пауза каждые 40 запросов
            if (i + 1) % 20 == 0:
                results += await asyncio.gather(*tasks)
                tasks = []
                await asyncio.sleep(1)  # пауза 1 секунда

        # Завершение оставшихся задач
        if tasks:
            results += await asyncio.gather(*tasks)

    print("Запросы завершены")
    return results


# Загрузка CSV и обновление
def enrich_dataframe(df: DataFrame):
    results = asyncio.run(fetch_all(df))
    result_df = pd.DataFrame(results)
    enriched_df = df.merge(result_df, on="tmdbId", how="left")
    return enriched_df


# Пример использования
if __name__ == "__main__":
    df = pd.read_csv("data/movies.csv", encoding="utf-8")
    # df_links = pd.read_csv("data/links.csv", encoding="utf-8")

    # df["genres"] = df["genres"].str.split("|")
    # df["year"] = df["title"].str.extract(r"\((\d{4})\)")
    # df["title"] = df["title"].str[:-7]
    # df["tmdbId"] = df_links["tmdbId"]

    enriched_df = enrich_dataframe(df)
    enriched_df.to_csv("data/movies_enriched.csv", index=False, encoding="utf-8")
    print("Готово: enriched_df сохранён в movies_enriched.csv")
