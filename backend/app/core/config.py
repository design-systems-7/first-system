import json
from pathlib import Path
from typing import Any, Literal, Type, Tuple, Dict

from pydantic import (
    PostgresDsn,
    computed_field, TypeAdapter, )
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource

from app.schemas.order import OrderData, ZoneData, ExecuterProfile, TollRoadsData, ConfigMap
from app.schemas.requests_config import HTTPDataSourceConfig


class ExternalConfigServiceSource(PydanticBaseSettingsSource):

    # These two are abstract methods from parent class
    def get_field_value(self, **kwargs) -> None:
        pass

    def prepare_field_value(self, value: dict, **kwargs) -> HTTPDataSourceConfig:
        return TypeAdapter(HTTPDataSourceConfig).validate_python(value)

    def __call__(self) -> Dict[str, Any]:
        encoding = self.config.get('env_file_encoding')
        file_content_json = json.loads(
            # Use top level json file (one level above ./backend/)
            Path('data_sources_config.json').read_text(encoding)
        )
        data_requests_config: dict[str, HTTPDataSourceConfig] = {}
        for data_source in file_content_json["data_sources"]:
            source_config_data = file_content_json["data_sources"][data_source]
            data_requests_config[data_source] = self.prepare_field_value(source_config_data)

        return {"DATA_REQUESTS_CONFIG": data_requests_config}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    PROJECT_NAME: str = "Service 1"
    POSTGRES_SERVER: str = "localhost"

    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "changethis"
    POSTGRES_DB: str = "app"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    TASK_WAIT_BEFORE_RETRY_IN_SECONDS: int = 10

    CONFIGS_URL: str
    DATA_REQUESTS_RESPONSES_SCHEMAS: dict[str, Type] = {
        "order_data": OrderData,
        "zone_data": ZoneData,
        "executer_profile": ExecuterProfile,
        "toll_roads": TollRoadsData,
        "configs": ConfigMap,
    }
    DATA_REQUESTS_CONFIG: dict[str, HTTPDataSourceConfig]
    CONFIGS_CACHE_UPDATE_EVERY_SECONDS: int = 60
    GLOBAL_HTTP_REQUEST_TIMEOUT: int = 10
    GLOBAL_HTTP_REQUEST_RETRIES: int = 1

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            ExternalConfigServiceSource(settings_cls),
            env_settings,
            file_secret_settings,
        )


settings = Settings()  # type: ignore
