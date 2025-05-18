from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()


class ApiConfig(BaseModel):
    port: int = 8000
    host: str = f"http://127.0.0.1:{port}"
    url: str = f"{host}/api"


class BotConfig(BaseModel):
    token: str


class Settings(BaseSettings):
    api: ApiConfig = ApiConfig()
    bot: BotConfig

    model_config = SettingsConfigDict(
        env_file=("../.env.example", "../.env"),
        env_nested_delimiter="__",
        case_sensitive=False,
    )


settings = Settings()  # type: ignore[call-arg]
