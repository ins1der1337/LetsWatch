import asyncio
import os
import pandas as pd
import aiohttp
from aiohttp import ClientSession
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from core.config import settings

BASE_URL = "https://api.themoviedb.org/3/movie"
API_KEY = settings.tmdb.api_key

# Файл для сохранения промежуточных результатов и отслеживания прогресса
PROGRESS_FILE = "data/movies_enriched_temp.csv"
PROCESSED_IDS_FILE = "data/processed_tmdb_ids.txt"  # Для хранения обработанных ID


class MovieDataRead(BaseModel):
    tmdb_id: int
    title: str = Field(max_length=256)
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
    director_obj = next(
        (person for person in crew if person.get("job") == "Director"), None
    )
    director: Optional[str] = director_obj["name"] if director_obj else None

    release_date: Optional[str] = movie_data.get("release_date", None)
    year: Optional[int] = int(release_date.split("-")[0]) if release_date else None

    overview_sentences = movie_data.get("overview", "").split(".")
    description = ".".join(overview_sentences[:2]).strip()
    if description and not description.endswith(".") and overview_sentences[:2]:
        description += "."

    movie = {
        "tmdb_id": tmdb_id,
        "title": movie_data.get("title", ""),
        "description": description if description else None,
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
        movie_url = f"{BASE_URL}/{tmdb_id}?language=ru"
        credits_url = f"{BASE_URL}/{tmdb_id}/credits?language=ru"

        headers = {"accept": "application/json", "Authorization": f"Bearer {API_KEY}"}

        movie_resp, credits_resp = await asyncio.gather(
            session.get(movie_url, headers=headers),
            session.get(credits_url, headers=headers),
        )

        # Проверяем статус-коды перед парсингом JSON
        movie_resp.raise_for_status()
        credits_resp.raise_for_status()

        movie_data = await movie_resp.json()
        credits_data = await credits_resp.json()

        movie = form_movie_data(tmdb_id, movie_data, credits_data)
        print(f"Фильм {movie.title} (ID: {tmdb_id}) успешно прошел валидацию")
        return movie

    except aiohttp.ClientResponseError as e:
        print(
            f"Ошибка HTTP при запросе фильма {tmdb_id}: {e.status} - {e.message}. URL: {e.request_info.url}"
        )
        return None
    except aiohttp.ClientError as e:
        print(f"Ошибка сети при запросе фильма {tmdb_id}: {e}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка при запросе фильма {tmdb_id}: {e}")
        return None


async def fetch_all(df: pd.DataFrame):
    processed_tmdb_ids = set()
    partial_results: List[Dict[str, Any]] = []

    # 1. Загружаем ранее обработанные ID и частичные результаты, если они есть
    if os.path.exists(PROCESSED_IDS_FILE):
        with open(PROCESSED_IDS_FILE, "r") as f:
            for line in f:
                try:
                    processed_tmdb_ids.add(int(line.strip()))
                except ValueError:
                    continue  # Пропускаем некорректные строки

    if os.path.exists(PROGRESS_FILE):
        try:
            partial_df = pd.read_csv(PROGRESS_FILE, encoding="utf-8")
            partial_results = partial_df.to_dict(orient="records")
            print(f"Загружено {len(partial_results)} ранее обработанных фильмов.")
            # Дополнительно убедимся, что ID из partial_results добавлены в processed_tmdb_ids
            for res in partial_results:
                if "tmdb_id" in res:
                    processed_tmdb_ids.add(res["tmdb_id"])
        except pd.errors.EmptyDataError:
            print("Временный файл пуст, начинаем с нуля.")
        except Exception as e:
            print(f"Ошибка при загрузке временного файла: {e}. Начинаем с нуля.")

    # Фильтруем tmdbId, которые уже были обработаны
    tmdb_ids_to_process = [
        tmdb_id
        for tmdb_id in df["tmdbId"].tolist()
        if tmdb_id not in processed_tmdb_ids
    ]
    print(
        f"Всего TMDB ID для обработки: {len(df['tmdbId']) - len(processed_tmdb_ids)} из {len(df['tmdbId'])}"
    )

    if not tmdb_ids_to_process:
        print("Все фильмы уже обработаны.")
        return partial_results  # Возвращаем уже загруженные данные

    connector = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        batch_size = 50  # Размер пачки для сохранения прогресса
        for i, tmdb_id in enumerate(tmdb_ids_to_process):
            tasks.append(fetch_movie_data(session, tmdb_id))

            # Сохраняем прогресс каждые 'batch_size' задач
            if (i + 1) % batch_size == 0 or (i + 1) == len(tmdb_ids_to_process):
                print(
                    f"Обработка пачки {int((i + 1) / batch_size)}/{int(len(tmdb_ids_to_process) / batch_size) + 1}..."
                )
                current_batch_results = await asyncio.gather(
                    *tasks, return_exceptions=True
                )
                tasks = []  # Очищаем задачи для следующей пачки

                # Добавляем результаты в список
                for res in current_batch_results:
                    if isinstance(res, MovieDataRead):
                        partial_results.append(res.model_dump())
                        # Добавляем успешно обработанный ID в наш набор
                        processed_tmdb_ids.add(res.tmdb_id)

                # Сохраняем промежуточные результаты
                temp_df = pd.DataFrame(partial_results)
                temp_df.to_csv(PROGRESS_FILE, index=False, encoding="utf-8")
                # Сохраняем список обработанных ID
                with open(PROCESSED_IDS_FILE, "w") as f:
                    for _id in processed_tmdb_ids:
                        f.write(f"{_id}\n")
                print(
                    f"Прогресс сохранен. Обработано {len(processed_tmdb_ids)} фильмов."
                )

    print("Все запросы завершены.")
    return partial_results


def enrich_dataframe(df: pd.DataFrame):
    if "tmdbId" not in df.columns:
        print("ВНИМАНИЕ: Колонка 'tmdbId' не найдена. Не могу продолжить без TMDB ID.")
        return None

    # Запускаем асинхронную функцию
    results_dicts = asyncio.run(fetch_all(df))

    # Объединяем результаты
    if not results_dicts:
        print("Нет данных для объединения.")
        return df

    result_df = pd.DataFrame(results_dicts)

    # Важно: имя колонки 'tmdb_id' в result_df должно совпадать с 'tmdbId' в исходном df
    # для корректного слияния. Переименуем, если нужно.
    if "tmdb_id" in result_df.columns and "tmdbId" not in result_df.columns:
        result_df.rename(columns={"tmdb_id": "tmdbId"}, inplace=True)

    # Удаляем дубликаты, если из-за возобновления в partial_results попали одни и те же ID
    result_df.drop_duplicates(subset="tmdbId", inplace=True)

    # Используем `merge` для добавления новых колонок к исходному DataFrame
    # Это перезапишет существующие колонки, если они есть в result_df
    enriched_df = df.merge(
        result_df, on="tmdbId", how="left", suffixes=("_original", "")
    )

    # Удаляем временные файлы после успешного завершения
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
    if os.path.exists(PROCESSED_IDS_FILE):
        os.remove(PROCESSED_IDS_FILE)
    print("Временные файлы удалены.")

    return enriched_df


if __name__ == "__main__":
    df = pd.read_csv("data/movies.csv", encoding="utf-8")

    # Пример, как получить tmdbId, если его нет напрямую в movies.csv
    # Вам нужно будет адаптировать это под вашу структуру данных
    # Если tmdbId уже есть в movies.csv, эти строки не нужны.
    if "tmdbId" not in df.columns:
        if os.path.exists("data/links.csv"):
            df_links = pd.read_csv("data/links.csv", encoding="utf-8")
            # Предполагаем, что 'movieId' в movies.csv соответствует 'movieId' в links.csv
            # и links.csv содержит 'tmdbId'
            df = df.merge(df_links[["movieId", "tmdbId"]], on="movieId", how="left")
            # Удаляем строки, где tmdbId не найден (NaN)
            df.dropna(subset=["tmdbId"], inplace=True)
            df["tmdbId"] = df["tmdbId"].astype(int)
            print(
                f"TMDB IDs добавлены из links.csv. Количество фильмов с TMDB ID: {len(df)}"
            )
        else:
            print(
                "Файл links.csv не найден, и колонка 'tmdbId' отсутствует в movies.csv."
            )
            print(
                "Без TMDB ID продолжить невозможно. Убедитесь, что movies.csv или links.csv содержит 'tmdbId'."
            )
            exit()
    else:
        df["tmdbId"] = df["tmdbId"].fillna(-1).astype(int)
        df = df[df["tmdbId"] != -1]  # Удалить строки с -1, если они не нужны

    enriched_df = enrich_dataframe(df)

    if enriched_df is not None:
        output_file = "data/movies_enriched.csv"
        enriched_df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"Готово: enriched_df сохранён в {output_file}")
    else:
        print("Обогащение данных не завершено.")
