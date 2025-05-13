from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, PostgresDsn
from dotenv import load_dotenv


load_dotenv()


class RunApiConfig(BaseModel):
    """Конфигурация API"""

    host: str = "127.0.0.1"
    port: int = 8000


class BotConfig(BaseModel):
    """Конфигурация Телеграм-бота"""

    token: str


class AppDBConfig(BaseModel):
    """Конфигурация БД нашего приложения"""

    url: PostgresDsn
    echo: int = 0
    ...


class TMDPApiConfig(BaseModel):
    """Конфигурация внешней TMDB API"""

    base_url: str = "https://api.themoviedb.org/3/movie"
    api_key: str


class Settings(BaseSettings):
    """Общая конфигурация"""

    api: RunApiConfig = RunApiConfig()
    tmdb_api: TMDPApiConfig
    bot: BotConfig
    db: AppDBConfig

    model_config = SettingsConfigDict(
        env_file=("../.env.example", "../.env"),
        env_nested_delimiter="__",
        case_sensitive=False,
    )


settings = Settings()  # type: ignore[call-arg]
