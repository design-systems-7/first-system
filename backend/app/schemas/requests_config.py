from pydantic import ConfigDict, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from typing_extensions import TypedDict, NotRequired

from app.app_logger import logger


class DictConfigBase(TypedDict):
    __pydantic_config__ = ConfigDict(extra='forbid')  # noqa


class HTTPClientConfig(DictConfigBase):
    timeout: NotRequired[int]
    retries: NotRequired[int]


class FallbacksConfig(DictConfigBase):
    is_caching_enabled: bool
    cache_ttl: NotRequired[int]
    config_data: NotRequired[dict]
    is_fallback_to_config: bool
    fallback_service_url: NotRequired[str]
    is_fallback_to_another_service: bool

    @field_validator('is_fallback_to_config')
    def config_fallback_configured_properly(cls, v, info: FieldValidationInfo):  # noqa
        if v and "config_data" not in info.data:
            logger.info(info.data)
            raise ValueError('If enabled fallback to config, data in config must be specified')
        return v

    @field_validator('is_fallback_to_another_service')
    def fallback_service_configured_properly(cls, v, info: FieldValidationInfo):  # noqa
        if v and "fallback_service_url" not in info.data:
            logger.info(info.data)
            raise ValueError('If enabled fallback to another service, fallback service url must be specified')
        return v


class HTTPDataSourceConfig(DictConfigBase):
    endpoint: str
    http_client_config: NotRequired[HTTPClientConfig]
    fallbacks_config: FallbacksConfig
