import asyncio
import dataclasses
import json
from os import environ
from typing import Tuple, Optional, Any, TypeVar, Type
from urllib.parse import urlencode

import httpx
from aiocache import Cache
from httpx import AsyncHTTPTransport, AsyncClient

from app.app_logger import logger
from app.core.config import settings
from app.schemas.order import OrderData, ZoneData, ExecuterProfile, ConfigMap, TollRoadsData
from app.schemas.requests_config import HTTPClientConfig, FallbacksConfig, HTTPDataSourceConfig

# For annotating some generic class
T = TypeVar('T')


class DataSourceException(Exception):
    pass


class DataProvider:
    """A class that asynchronously fetches data needed to create an order from multiple data sources at once."""

    def __init__(self):
        self._cache = Cache(Cache.REDIS, endpoint='redis_cache', port=6379)

    async def collect_order_info(self, order_id: str, executer_id: str) -> Tuple[
        OrderData, ZoneData, ExecuterProfile, ConfigMap, TollRoadsData
    ]:
        order_data_task = self.fetch_with_fallback_strategy(data_source="order_data",
                                                            query_params={"id": order_id})
        executer_profile_task = self.fetch_with_fallback_strategy(data_source="executer_profile",
                                                                  query_params={"id": executer_id})
        # Configs source is special case. We fetch data only from cache - it is updated by periodic task
        configs_task = self.get_configs_data()

        order_data, executer_profile, configs = await asyncio.gather(
            order_data_task, executer_profile_task, configs_task
        )

        zone_data = await self.fetch_with_fallback_strategy(data_source="zone_data",
                                                            query_params={"id": order_data.zone_id})
        toll_roads_data = await self.fetch_with_fallback_strategy(data_source="toll_roads",
                                                                  query_params={
                                                                      "zone_display_name": zone_data.display_name
                                                                  })

        return order_data, zone_data, executer_profile, configs, toll_roads_data

    async def fetch_with_fallback_strategy(self, data_source: str,
                                           query_params: Optional[dict[str, Any]] = None,
                                           ) -> T:
        # CamelCase to more explicit indication that this is a class
        ResponseSchema: Type[T] = settings.DATA_REQUESTS_RESPONSES_SCHEMAS[data_source]  # noqa
        data_source_requests_config: HTTPDataSourceConfig = settings.DATA_REQUESTS_CONFIG[data_source]

        # TODO вернуть ояьбзательный fallabck_config
        timeout: int = data_source_requests_config.get("http_client_config", {}).get(
            "timeout", settings.GLOBAL_HTTP_REQUEST_TIMEOUT
        )
        retries: int = data_source_requests_config.get("http_client_config", {}).get(
            "retries", settings.GLOBAL_HTTP_REQUEST_RETRIES
        )

        fallbacks_config: FallbacksConfig = data_source_requests_config["fallbacks_config"]
        is_caching_enabled: bool = fallbacks_config["is_caching_enabled"]
        cache_ttl: int = fallbacks_config.get("cache_ttl", None)
        is_fallback_to_config: bool = fallbacks_config["is_fallback_to_config"]
        config_data: dict = fallbacks_config.get("config_data", None)

        url: str = data_source_requests_config['endpoint']
        if query_params is not None:
            url += "?" + urlencode(query_params)

        result = await self.fetch_from_data_source(ResponseSchema=ResponseSchema,
                                                   url=url, timeout=timeout, retries=retries,
                                                   is_caching_enabled=is_caching_enabled, cache_ttl=cache_ttl)

        if result is None and is_caching_enabled:
            result = await self.fetch_from_cache(ResponseSchema=ResponseSchema, url=url)

        if result is None and is_fallback_to_config:
            result = ResponseSchema(**config_data)

        if result is None:
            # TODO Catch it on API level to return proper HTTPResponse
            # TODO Also catch all other exceptions -- for exaample, if service give us wrong response format,
            #  dataclass will throw some exception. We want this and want to give pretty same error "data source broken"
            raise DataSourceException(f"Missing data from {data_source}.")

        logger.info(f'Got data from {data_source}: {result}')
        return result

    async def fetch_from_data_source(self, ResponseSchema: Type[T],
                                     url: str,
                                     timeout: int,
                                     retries: int,
                                     is_caching_enabled: bool, cache_ttl: Optional[int]) -> Optional[T]:
        transport = AsyncHTTPTransport(retries=retries)
        try:
            async with AsyncClient(transport=transport) as client:
                result = await client.get(url, timeout=timeout)
                result = result.raise_for_status()
                result = ResponseSchema(**result.json())
        except Exception as e:
            logger.error(f"Fetching with {url} directly failed: {e}")
            return None

        if is_caching_enabled:
            try:
                await self._cache.set(url, json.dumps(dataclasses.asdict(result)), ttl=cache_ttl)
            except Exception as e:
                logger.error(f"Error during caching from {url}: {e}")

        return result

    async def fetch_from_cache(self, ResponseSchema: Type[T],
                               url: str) -> Optional[T]:
        cached_response = await self._cache.get(url)
        if cached_response is not None:
            response = ResponseSchema(**json.loads(cached_response))
            return response
        return None

    async def get_configs_data(self) -> ConfigMap:
        cached_response = await self._cache.get(settings.CONFIGS_URL)
        if cached_response is not None:
            data = json.loads(cached_response)
            logger.info(f'Got data from configs: {data}')
            return ConfigMap(data)
        # Highly unexpected case - possible only with cache corruption
        raise DataSourceException("Missing config data in cache!")

    async def update_config_cache(self) -> bool:
        url: str = settings.CONFIGS_URL
        transport = AsyncHTTPTransport(retries=settings.GLOBAL_HTTP_REQUEST_RETRIES)
        try:
            async with AsyncClient(transport=transport) as client:
                config_response = await client.get(url, timeout=settings.GLOBAL_HTTP_REQUEST_TIMEOUT)
                config_response.raise_for_status()
                await self._cache.set(url, json.dumps(config_response.json()))
        except httpx.HTTPError as exc:
            logger.error(f"HTTP Exception during request to config service {exc.request.url} - {exc}")
            return False
        except Exception as exc:
            logger.error(f"Error during updating config cache: {exc}")
            return False

        return True
