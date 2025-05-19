from pathlib import Path

import pandas as pd
from pandas.core.frame import DataFrame, Series

from api.exceptions import BadRequestException
from core.config import settings
from core.schemas.movies import PaginationParams, MovieReadSchema, MoviesResponseSchema


class MovieRepository:

    def __init__(self, movies_path: Path):
        self.df: DataFrame = pd.read_csv(movies_path, encoding="utf-8")
        self._init_dataframe()

    def _init_dataframe(self):
        self.df = self.df.drop_duplicates(subset=["tmdbId", "title"])
        self.df = self.df.reset_index(drop=True)
        self.df = self.df.drop(columns=["Unnamed: 0", "tmdbId"])

    @staticmethod
    def _validate_dataframe(df) -> list[MovieReadSchema]:
        movie_list = []

        for _, row in df.iterrows():
            genres = [
                str(genre)
                for genre in row["genres"]
                .strip("[]")
                .replace("'", "")
                .replace(" ", "")
                .split(",")
            ]

            movie_data = {
                "movieId": row["movieId"],
                "title": row["title"],
                "genres": genres,
                "description": (
                    row["description"] if type(row["description"]) != float else None
                ),
                "year": int(row["year"]),
                "poster_url": row["poster_url"],
                "director": row["director"],
                "actors": [actor.strip() for actor in row["actors"].split(",")],
            }
            movie_list.append(MovieReadSchema.model_validate(movie_data))

        return movie_list

    def search_by_title(
        self, title: str, pagination: PaginationParams
    ) -> MoviesResponseSchema:
        filtered_df: Series = self.df[
            self.df["title"].str.contains(title, case=False, na=False)
        ]
        count = len(filtered_df)

        if pagination.page > count:
            raise BadRequestException("Дальше страниц нет")

        filtered_df = filtered_df.iloc[
            (pagination.page - 1) * pagination.limit :
            pagination.limit + (pagination.page - 1) * pagination.limit
        ]
        movies = self._validate_dataframe(filtered_df)

        return MoviesResponseSchema(movies=movies, pagination=pagination, totalMovies=count)

    def search_by_genre(
        self, genre: str, pagination: PaginationParams
    ) -> MoviesResponseSchema:
        filtered_df: Series = self.df[
            self.df["genres"].str.contains(genre, case=False, na=False)
        ]
        count = len(filtered_df)

        if pagination.page > count:
            raise BadRequestException("Дальше страниц нет")

        filtered_df = filtered_df.iloc[
                      (pagination.page - 1) * pagination.limit:
                      pagination.limit + (pagination.page - 1) * pagination.limit
                      ]
        movies = self._validate_dataframe(filtered_df)

        return MoviesResponseSchema(movies=movies, pagination=pagination, totalMovies=count)

    def search_by_actor(
        self, actor: str, pagination: PaginationParams
    ) -> MoviesResponseSchema:
        filtered_df: Series = self.df[
            self.df["actors"].str.contains(actor, case=False, na=False)
        ]
        count = len(filtered_df)

        if pagination.page > count:
            raise BadRequestException("Дальше страниц нет")

        filtered_df = filtered_df.iloc[
                      (pagination.page - 1) * pagination.limit:
                      pagination.limit + (pagination.page - 1) * pagination.limit
                      ]
        movies = self._validate_dataframe(filtered_df)

        return MoviesResponseSchema(movies=movies, pagination=pagination, totalMovies=count)


movie_db = MovieRepository(movies_path=settings.movie.movie_data)
