from pathlib import Path

import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

movies_path = Path(__file__).parent.parent.parent / "data" / "movies_main.csv"


df: DataFrame = pd.read_csv(movies_path, encoding="utf-8")
df = df.drop_duplicates(subset=["tmdbId", "title"])
df = df.reset_index(drop=True)
df = df.drop(columns=["Unnamed: 0", "tmdbId"])


def search_by_name(title: str):
    iltered_df = df[df["title"].str.contains(title, case=False, na=False)]
    iltered_df = iltered_df.sort_values(by="rating", ascending=False)
    return iltered_df.head(5)


def search_by_genre(genre: str):
    iltered_df = df[df["genres"].str.contains(genre, case=False, na=False)]
    iltered_df = iltered_df.sort_values(by="rating", ascending=False)
    return iltered_df.head(5)


def combine_features(row):
    return " ".join(
        [
            str(row["genres"]),
            str(row["actors"]),
            str(row["director"]),
        ]
    )


# Подготовка модели
def prepare_model(df):
    df = df.dropna(subset=["genres", "actors", "director", "description"]).copy()
    df["combined"] = df.apply(combine_features, axis=1)

    # Векторизация признаков (TF-IDF)
    vectorizer = TfidfVectorizer(stop_words="english", max_features=10000)
    tfidf_matrix = vectorizer.fit_transform(df["combined"])

    # Модель ближайших соседей
    nn_model = NearestNeighbors(metric="cosine", algorithm="brute")
    nn_model.fit(tfidf_matrix)

    return df, tfidf_matrix, nn_model, vectorizer


# Поиск похожих фильмов по названию
def recommend_by_title(title, df, tfidf_matrix, nn_model, vectorizer, n=5):
    if not df["title"].isin([title]).any():
        return f"Фильм '{title}' не найден."

    idx = df[df["title"] == title].index[0]
    distances, indices = nn_model.kneighbors(tfidf_matrix[idx], n_neighbors=n + 1)

    # Исключаем сам фильм (первый)
    similar_indices = indices[0][1:]
    recommended_movies_df = df.iloc[similar_indices]
    return recommended_movies_df.to_json(orient="records", force_ascii=False, indent=4)


df, tfidf_matrix, nn_model, vectorizer = prepare_model(df)

# Получить рекомендации
recommendations = recommend_by_title("Toy Story", *prepare_model(df))
print(recommendations)
