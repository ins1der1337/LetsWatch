from pathlib import Path
from typing import Optional

import pandas as pd
from pandas import Series
from pandas.core.frame import DataFrame
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

from api.exceptions import BadRequestException, NotFoundException
from core.config import settings
from core.schemas.movies import PaginationParams, MovieReadSchema, MoviesResponseSchema


class MovieRepository:

    def __init__(self, movies_path: Path):
        self.df: DataFrame = pd.read_parquet(movies_path)
        self._init_dataframe()

    def _init_dataframe(self):
        self.df = self.df.drop_duplicates(subset=["tmdbId", "title"])
        self.df = self.df.reset_index(drop=True)
        self.df = self.df.drop(columns="tmdbId")
        self.df = self.df.sort_values(by=["rating_counts", "rating"], ascending=False)

    def _process_movie_response(
        self, df: DataFrame, pagination: Optional[PaginationParams] = None
    ) -> MoviesResponseSchema:
        count = len(df)
        if count == 0:
            raise NotFoundException("По вашему запросу ничего не найдено")

        if pagination:
            df = self._pagination_apply(df, pagination)

        movies = self._validate_dataframe(df)
        return MoviesResponseSchema(
            movies=movies, pagination=pagination, totalMovies=count
        )

    @staticmethod
    def _validate_dataframe(df: DataFrame) -> list[MovieReadSchema]:
        movie_list = []

        for _, row in df.iterrows():
            if pd.notna(row["genres"]):
                genres = [
                    str(genre).strip(" ")
                    for genre in row["genres"].strip("[]").replace("'", "").split(",")
                ]
            else:
                genres = []

            if pd.notna(row["actors"]):
                actors = [
                    str(actor).strip(" ")
                    for actor in row["actors"].strip("[]").replace("'", "").split(",")
                ]
            else:
                actors = []

            movie_data = {
                "movie_id": row["movieId"],
                "title": row["title"],
                "genres": genres if pd.notna(row["genres"]) else None,
                "description": (
                    str(row["description"]) if pd.notna(row["description"]) else None
                ),
                "year": int(row["year"]) if pd.notna(row["year"]) else None,
                "rating": float(row["rating"]) if pd.notna(row["rating"]) else None,
                "rating_counts": (
                    int(row["rating_counts"])
                    if pd.notna(row["rating_counts"])
                    else None
                ),
                "poster_url": (
                    row["poster_url"] if pd.notna(row["poster_url"]) else None
                ),
                "director": row["director"] if pd.notna(row["director"]) else None,
                "actors": actors if pd.notna(row["actors"]) else None,
            }
            movie_list.append(MovieReadSchema.model_validate(movie_data))

        return movie_list

    @staticmethod
    def _pagination_apply(df: DataFrame, pagination: PaginationParams) -> DataFrame:
        if pagination.page > len(df):
            raise BadRequestException("Дальше страниц нет")

        df = df.iloc[
            (pagination.page - 1) * pagination.limit : pagination.limit
            + (pagination.page - 1) * pagination.limit
        ]
        return df

    @staticmethod
    def normalize_text(text):
        if isinstance(text, str):
            return text.replace('ё', 'е').replace('Ё', 'Е')
        return text


class SearchModelRepository(MovieRepository):

    def __init__(self, movies_path: Path):
        super().__init__(movies_path)

    def search_movies(
        self,
        pagination: PaginationParams,
        title: Optional[str] = None,
        genre: Optional[str] = None,
        actor: Optional[str] = None,
        director: Optional[str] = None,
    ) -> MoviesResponseSchema:
        temp_df = self.df.copy()

        if title:
            title = self.normalize_text(title)
            temp_df = temp_df[
                temp_df["title"]
                .apply(self.normalize_text)
                .str.contains(title, case=False, na=False)
            ]
        if genre:
            genre = self.normalize_text(genre)
            temp_df = temp_df[
                temp_df["genres"]
                .apply(self.normalize_text)
                .str.contains(genre, case=False, na=False)
            ]
        if actor:
            actor = self.normalize_text(actor)
            temp_df = temp_df[
                temp_df["actors"]
                .apply(self.normalize_text)
                .str.contains(actor, case=False, na=False)
            ]
        if director:
            director = self.normalize_text(director)
            temp_df = temp_df[
                temp_df["director"]
                .apply(self.normalize_text)
                .str.contains(director, case=False, na=False)
            ]

        return self._process_movie_response(temp_df, pagination)

    def search_movie_by_movie_id(self, movie_id: int) -> MoviesResponseSchema:
        temp_df: DataFrame = self.df.copy()
        temp_df = temp_df.loc[temp_df["movieId"] == movie_id]
        return self._process_movie_response(temp_df)


class RecommendModelRepository(MovieRepository):

    def __init__(self, movies_path: Path):
        super().__init__(movies_path)
        self._recommend_model: Optional[DataFrame] = None
        self._tfidf_matrix = None
        self._nn_model = None
        self._vectorizer = None
        self._prepare_model()

    @staticmethod
    def _combine_features(row: Series):
        return " ".join(
            [
                str(row["genres"]),
                str(row["actors"]),
                str(row["director"]),
            ]
        )

    def _prepare_model(self) -> None:
        temp_df: DataFrame = self.df.copy()
        temp_df = temp_df.dropna(
            subset=["genres", "actors", "director", "description"]
        ).copy()
        temp_df["combined"] = temp_df.apply(self._combine_features, axis=1)

        self._recommend_model = temp_df.reset_index(drop=True)

        # Векторизация признаков (TF-IDF)
        self._vectorizer = TfidfVectorizer(stop_words="english", max_features=10000)
        self._tfidf_matrix = self._vectorizer.fit_transform(temp_df["combined"])

        # Модель ближайших соседей
        self._nn_model = NearestNeighbors(metric="cosine", algorithm="brute")
        self._nn_model.fit(self._tfidf_matrix)

    def recommend_movies_by_title(
        self,
        title: str,
        pagination: PaginationParams,
    ) -> MoviesResponseSchema:

        if (
            self._recommend_model is None
            or self._nn_model is None
            or self._tfidf_matrix is None
        ):
            raise NotFoundException("Рекомендательная система не работает")

        movie_candidates = self._recommend_model[
            self._recommend_model["title"].apply(self.normalize_text).str.lower() == title.lower()
        ]

        if movie_candidates.empty:
            raise NotFoundException(
                f"Фильм '{title}' не найден в базе данных для предоставления рекомендаций."
            )

        movie_index_in_recommend_df = movie_candidates.index[0]

        distances, indices = self._nn_model.kneighbors(
            self._tfidf_matrix[movie_index_in_recommend_df],
            n_neighbors=100 + 1,
        )

        similar_indices = indices[0][1:]

        if len(similar_indices) == 0:
            raise NotFoundException(f"Не найдено рекомендаций для фильма '{title}'.")

        # Исключаем сам фильм (первый)
        similar_indices = indices[0][1:]
        recommended_movies_df = self._recommend_model.iloc[similar_indices].copy()

        return self._process_movie_response(recommended_movies_df, pagination)


search_model = SearchModelRepository(movies_path=settings.movie.movie_data)
recommend_model = RecommendModelRepository(movies_path=settings.movie.movie_data)
