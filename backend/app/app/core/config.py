import pathlib
from pydantic import BaseSettings


class Settings(BaseSettings):
    # url naming: https://docs.sqlalchemy.org/en/20/core/engines.html#sqlite
    SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///app/storage/example.db"

    class Config:
        # case_sensitive: https://docs.pydantic.dev/usage/settings/#environment-variable-names
        case_sensitive = True

        # read settings from .env file
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings(_env_file=f'{pathlib.Path(__file__).parents[3].resolve()}/.env')
