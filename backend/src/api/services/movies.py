from pathlib import Path

import pandas as pd
from pandas.core.frame import DataFrame

from api.exceptions import BadRequestException, NotFoundException
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

    def search_by_title(
        self, title: str, pagination: PaginationParams
    ) -> MoviesResponseSchema:
        filtered_df = self.df[
            self.df["title"].str.contains(title, case=False, na=False)
        ]
        return self._process_movie_response(filtered_df, pagination)

    def search_by_genre(
        self, genre: str, pagination: PaginationParams
    ) -> MoviesResponseSchema:
        filtered_df = self.df[
            self.df["genres"].str.contains(genre, case=False, na=False)
        ]
        return self._process_movie_response(filtered_df, pagination)

    def search_by_actor(
        self, actor: str, pagination: PaginationParams
    ) -> MoviesResponseSchema:
        filtered_df = self.df[
            self.df["actors"].str.contains(actor, case=False, na=False)
        ]
        return self._process_movie_response(filtered_df, pagination)

    def _process_movie_response(
        self, df: DataFrame, pagination: PaginationParams
    ) -> MoviesResponseSchema:
        count = len(df)
        if count == 0:
            raise NotFoundException("По вашему запросу ничего не найдено")

        df = self._pagination_apply(df, pagination)
        movies = self._validate_dataframe(df)
        return MoviesResponseSchema(
            movies=movies, pagination=pagination, totalMovies=count
        )

    @staticmethod
    def _validate_dataframe(df: DataFrame) -> list[MovieReadSchema]:
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

    @staticmethod
    def _pagination_apply(df: DataFrame, pagination: PaginationParams) -> DataFrame:
        if pagination.page > len(df):
            raise BadRequestException("Дальше страниц нет")

        df = df.iloc[
             (pagination.page - 1) * pagination.limit: pagination.limit
                                                       + (pagination.page - 1) * pagination.limit
             ]
        return df


movie_db = MovieRepository(movies_path=settings.movie.movie_data)
