from pathlib import Path

import pandas as pd
from pandas.core.frame import DataFrame, Series

from core.config import settings
from core.schemas.movies import PaginationParams


class MovieRepository:

    def __init__(self, movies_path: Path):
        self.df: DataFrame = pd.read_csv(movies_path, encoding="utf-8")
        self._init_dataframe()

    def _init_dataframe(self):
        self.df = self.df.drop_duplicates(subset=["tmdbId", "title"])
        self.df = self.df.reset_index(drop=True)
        self.df = self.df.drop(columns=["Unnamed: 0", "tmdbId"])

    def search_by_title(self, title: str, pagination: PaginationParams):
        filtered_df: Series = self.df[self.df["title"].str.contains(title, case=False, na=False)]
        filtered_df = filtered_df.head(pagination.limit)
        return filtered_df.to_json(orient="records", force_ascii=False, indent=4)

    def search_by_genre(self, genre: str, pagination: PaginationParams):
        filtered_df: Series = self.df[self.df["genres"].str.contains(genre, case=False, na=False)]
        filtered_df = filtered_df.head(pagination.limit)
        return filtered_df.to_json(orient="records", force_ascii=False, indent=4)


movie_db = MovieRepository(movies_path=settings.movie.movie_data)
