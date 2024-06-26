from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASEDIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    STATE_FILE_NAME: str
    ELASTIC_HOST: str
    ELASTIC_PORT: int
    ELASTIC_SCHEMA: str

    model_config = SettingsConfigDict(env_file=BASEDIR / '.env')


app_settings = Settings()
