import pandas as pd
from core.database import db_helper

df = pd.read_csv("movies_main.csv")


async def make_movies_model():
    res = df.to_sql("movies", db_helper.get_engine)


if __name__ == "__main__":
    print(f"{res = }")
