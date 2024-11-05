import dataclasses
import json
from os import environ
from typing import Tuple
from urllib.parse import urlencode

import httpx
import asyncio
from aiocache import Cache

from app.app_logger import logger
from app.core.config import settings
from app.schemas.order import OrderData, ZoneData, ExecuterProfile, ConfigMap, TollRoadsData



class DataProvider:
    """A class that asynchronously fetches data needed to create an order from multiple data sources at once."""

    def __init__(self):
        self._cache = Cache(Cache.REDIS, endpoint='redis_cache', port=6379)

    async def fetch_order_info(self, order_id: str, executer_id: str) -> Tuple[
        OrderData, ZoneData, ExecuterProfile, ConfigMap, TollRoadsData
    ]:
        async with httpx.AsyncClient() as client:
            order_data_task = self.get_order_data(client, order_id)
            executer_profile_task = self.get_executer_profile(client, executer_id)
            configs_task = self.get_configs(client)

            order_data, executer_profile, configs = await asyncio.gather(
                order_data_task, executer_profile_task, configs_task
            )

            zone_data = await self.get_zone_data(client, order_data.zone_id)

            toll_roads_data = await self.get_toll_roads(client, zone_data.display_name)

            return order_data, zone_data, executer_profile, configs, toll_roads_data

    async def get_order_data(self, client: httpx.AsyncClient, order_id: str) -> OrderData:
        url = environ.get('ORDER_DATA_ENDPOINT') + '?' + urlencode({'id': order_id})
        response = await client.get(url)
        response_data = response.json()
        return OrderData(
            id=order_id,
            zone_id=response_data['zone_id'],
            user_id=response_data['user_id'],
            base_coin_amount=response_data['base_coin_amount']
        )

    # LRU-cache with 10 minute ttl
    async def get_zone_data(self, client: httpx.AsyncClient, zone_id: str) -> ZoneData:
        url = environ.get('ZONE_DATA_ENDPOINT') + '?' + urlencode({'id': zone_id})
        cached_response = await self._cache.get(url)
        if cached_response is not None:
            zone_data = ZoneData(**json.loads(cached_response))
            logger.info(f'Zone data cached response: {zone_data}')
            return zone_data
        response = await client.get(url)
        response_data = response.json()

        zone_data = ZoneData(
            id=zone_id,
            coin_coeff=response_data['coin_coeff'],
            display_name=response_data['display_name']
        )

        # пока оставляю здесь магическое число, потому что в будущем хочу переделать то, как сейчас все происходит
        await self._cache.set(url, json.dumps(dataclasses.asdict(zone_data)), ttl=10 * 60)

        return zone_data

    async def get_executer_profile(self, client: httpx.AsyncClient, executer_id: str) -> ExecuterProfile:
        url = environ.get('EXECUTER_PROFILE_ENDPOINT') + '?' + urlencode({'id': executer_id})
        response = await client.get(url)
        response_data = response.json()
        return ExecuterProfile(
            id=executer_id,
            tags=response_data['tags'],
            rating=response_data['rating']
        )

    # Cache refreshed every minute
    async def get_configs(self, client: httpx.AsyncClient) -> ConfigMap:
        url = environ.get('CONFIGS_ENDPOINT')

        cached_response = await self._cache.get(url)
        if cached_response is not None:
            data = json.loads(cached_response)
            logger.info(f'Config Map cached response: {data}')
            return ConfigMap(data)
        raise Exception

    async def get_toll_roads(self, client: httpx.AsyncClient, zone_display_name: str) -> TollRoadsData:
        url = environ.get('TOLLROADS_ENDPOINT') + '?' + urlencode({'zone_display_name': zone_display_name})
        cached_response = await self._cache.get(url)
        if cached_response is not None:
            tolls_data = TollRoadsData(**json.loads(cached_response))
            logger.info(f'Cached toll roads data: {tolls_data}')
            return tolls_data
        response = await client.get(url)
        response_data = response.json()
        tolls_data = TollRoadsData(
            response_data['bonus_amount']
        )

        # TODO: add fallback to config

        await self._cache.set(url, json.dumps(dataclasses.asdict(tolls_data)))

        return tolls_data

    async def update_config_cache(self) -> None:
        url = environ.get('CONFIGS_ENDPOINT')
        try:
            config_response = httpx.get(url).raise_for_status()
            await self._cache.set(url, json.dumps(config_response.json()))
        except httpx.HTTPError as exc:
            logger.error(f"HTTP Exception during request to config service {exc.request.url} - {exc}")
            raise exc
        except Exception as exc:
            logger.error(f"Error during updating config cache: {exc}")
            raise exc
