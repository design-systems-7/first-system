from dataclasses import dataclass
from typing import Annotated, Any, Literal, Type

from pydantic import (
    AnyUrl,
    BeforeValidator,
    PostgresDsn,
    computed_field, TypeAdapter,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas.order import OrderData, ZoneData, ExecuterProfile, TollRoadsData, ConfigMap
from app.schemas.requests_config import HTTPDataSourceConfig

a = '''{
"endpoint": "http://external_apis:3629/order-data",
  "http_client_config": {
    "timeout": 30,
    "retries": 2
  },
  "fallbacks_config": {
    "is_caching_enabled": false,
    "is_fallback_to_config": false
  }
}'''
c = '''{
"endpoint": "http://external_apis:3629/zone-data",
  "fallbacks_config": {
    "is_caching_enabled": true,
    "cache_ttl": 600,
    "is_fallback_to_config": false
  }
}'''
d = '''{
"endpoint": "http://external_apis:3629/executer-profile",
  "http_client_config": {
    "timeout": 60,
    "retries": 1
  },
  "fallbacks_config": {
    "is_caching_enabled": false,
    "is_fallback_to_config": false
  }
}'''
e = '''{
"endpoint": "http://external_apis:3629/toll-roads",
  "fallbacks_config": {
    "is_caching_enabled": true,
    "is_fallback_to_config": true,
    "config_data": {
    "bonus_amount": 0
    }
  }
}'''


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in
                v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]

    PROJECT_NAME: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    CONFIGS_URL: str
    DATA_REQUESTS_RESPONSES_SCHEMAS: dict[str, Type] = {
        "order_data": OrderData,
        "zone_data": ZoneData,
        "executer_profile": ExecuterProfile,
        "toll_roads": TollRoadsData,
        "configs": ConfigMap,
    }
    DATA_REQUESTS_CONFIG: dict[str, HTTPDataSourceConfig] = {
        "order_data": TypeAdapter(HTTPDataSourceConfig).validate_json(a),
        "zone_data": TypeAdapter(HTTPDataSourceConfig).validate_json(c),
        "executer_profile": TypeAdapter(HTTPDataSourceConfig).validate_json(d),
        "toll_roads": TypeAdapter(HTTPDataSourceConfig).validate_json(e),
    }
    CONFIGS_CACHE_UPDATE_EVERY_SECONDS: int = 60
    GLOBAL_HTTP_REQUEST_TIMEOUT: int = 10
    GLOBAL_HTTP_REQUEST_RETRIES: int = 3

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

    CONFIG_CACHE_UPDATE_EVERY_SECONDS: int = 60


settings = Settings()  # type: ignore


# TODO Дописать json и поставить сюда заглушкой
# TODO Дописать остальную логику в data_provider
# TODO Parsing of json to custom source with DATA_SOURCE_MAPPING_TO_REQUEST_CONFIG
