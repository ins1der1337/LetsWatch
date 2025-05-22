from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class RunApiConfig(BaseModel):
    """Конфигурация API"""

    host: str = "127.0.0.1"
    port: int = 8000


class AppDBConfig(BaseModel):
    """Конфигурация БД нашего приложения"""

    url: PostgresDsn
    echo: int = 0


class MovieDbConfig(BaseModel):
    movie_data: Path = Path(__file__).parent.parent.parent / "data" / "movies.csv"


class Settings(BaseSettings):
    """Общая конфигурация"""

    api: RunApiConfig = RunApiConfig()
    movie: MovieDbConfig = MovieDbConfig()
    db: AppDBConfig

    model_config = SettingsConfigDict(
        env_file=("../.env.example", "../.env"),
        env_nested_delimiter="__",
        case_sensitive=False,
    )


settings = Settings()  # type: ignore[call-arg]
