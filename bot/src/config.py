from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()


class BotConfig(BaseModel):
    token: str


class Settings(BaseSettings):
    bot: BotConfig

    model_config = SettingsConfigDict(
        env_file=("../.env.example", "../.env"),
        env_nested_delimiter="__",
        case_sensitive=False,
    )


settings = Settings()  # type: ignore[call-arg]

print(settings.bot.token)