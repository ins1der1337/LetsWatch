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
        self.df: DataFrame = pd.read_csv(movies_path, encoding="utf-8")
        self._init_dataframe()

    def _init_dataframe(self):
        self.df = self.df.drop_duplicates(subset=["tmdbId", "title"])
        self.df = self.df.reset_index(drop=True)
        self.df = self.df.drop(columns=["Unnamed: 0", "tmdbId"])

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
                    str(row["description"]) if pd.notna(row["description"]) else None
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
            (pagination.page - 1) * pagination.limit : pagination.limit
            + (pagination.page - 1) * pagination.limit
        ]
        return df


class SearchModelRepository(MovieRepository):

    def __init__(self, movies_path: Path):
        super().__init__(movies_path)

    def search_movies(
        self,
        pagination: PaginationParams,
        title: Optional[str] = None,
        genre: Optional[str] = None,
        actor: Optional[str] = None,
    ) -> MoviesResponseSchema:
        temp_df = self.df.copy()

        if title:
            temp_df = temp_df[
                temp_df["title"].str.contains(title, case=False, na=False)
            ]
        if genre:
            temp_df = temp_df[
                temp_df["genres"].str.contains(genre, case=False, na=False)
            ]
        if actor:
            temp_df = temp_df[
                temp_df["actors"].str.contains(actor, case=False, na=False)
            ]

        return self._process_movie_response(temp_df, pagination)


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
            self._recommend_model["title"].str.lower() == title.lower()
        ]

        if movie_candidates.empty:
            raise NotFoundException(
                f"Фильм '{title}' не найден в базе данных для предоставления рекомендаций."
            )

        movie_index_in_recommend_df = movie_candidates.index[0]

        distances, indices = self._nn_model.kneighbors(
            self._tfidf_matrix[movie_index_in_recommend_df],
            n_neighbors=pagination.limit + 1,
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


# def combine_features(row):
#     return " ".join(
#         [
#             str(row["genres"]),
#             str(row["actors"]),
#             str(row["director"]),
#         ]
#     )
#
#
# # Подготовка модели
# def prepare_model(df):
#     df = df.dropna(subset=["genres", "actors", "director", "description"]).copy()
#     df["combined"] = df.apply(combine_features, axis=1)
#
#     # Векторизация признаков (TF-IDF)
#     vectorizer = TfidfVectorizer(stop_words="english", max_features=10000)
#     tfidf_matrix = vectorizer.fit_transform(df["combined"])
#
#     # Модель ближайших соседей
#     nn_model = NearestNeighbors(metric="cosine", algorithm="brute")
#     nn_model.fit(tfidf_matrix)
#
#     return df, tfidf_matrix, nn_model, vectorizer
#
#
# # Поиск похожих фильмов по названию
# def recommend_by_title(title, df, tfidf_matrix, nn_model, vectorizer, n=5):
#     if not df["title"].isin([title]).any():
#         return f"Фильм '{title}' не найден."
#
#     idx = df[df["title"] == title].index[0]
#     distances, indices = nn_model.kneighbors(tfidf_matrix[idx], n_neighbors=n + 1)
#
#     # Исключаем сам фильм (первый)
#     similar_indices = indices[0][1:]
#     recommended_movies_df = df.iloc[similar_indices]
#     return recommended_movies_df.to_json(orient="records", force_ascii=False, indent=4)
#
#
# df, tfidf_matrix, nn_model, vectorizer = prepare_model(df)
#
# # Получить рекомендации
# recommendations = recommend_by_title("Toy Story", *prepare_model(df))
# print(recommendations)
