from os import environ
from typing import Tuple
from urllib.parse import urlencode

import httpx
import asyncio

from app.schemas.order import OrderData, ZoneData, ExecuterProfile, ConfigMap, TollRoadsData


class DataProvider:
    """A class that asynchronously fetches data needed to create an order from multiple data sources at once."""

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


    async def get_zone_data(self, client: httpx.AsyncClient, zone_id: str) -> ZoneData:
        url = environ.get('ZONE_DATA_ENDPOINT') + '?' + urlencode({'id': zone_id})
        response = await client.get(url)
        response_data = response.json()
        return ZoneData(
            id=zone_id,
            coin_coeff=response_data['coin_coeff'],
            display_name=response_data['display_name']
        )


    async def get_executer_profile(self, client: httpx.AsyncClient, executer_id: str) -> ExecuterProfile:
        url = environ.get('EXECUTER_PROFILE_ENDPOINT') + '?' + urlencode({'id': executer_id})
        response = await client.get(url)
        response_data = response.json()
        return ExecuterProfile(
            id=executer_id,
            tags=response_data['tags'],
            rating=response_data['rating']
        )


    async def get_configs(self, client: httpx.AsyncClient) -> ConfigMap:
        url = environ.get('CONFIGS_ENDPOINT')
        response = await client.get(url)
        return ConfigMap(response.json())


    async def get_toll_roads(self, client: httpx.AsyncClient, zone_display_name: str) -> TollRoadsData:
        url = environ.get('TOLLROADS_ENDPOINT') + '?' + urlencode({'zone_display_name': zone_display_name})
        response = await client.get(url)
        response_data = response.json()
        return TollRoadsData(
            response_data['bonus_amount']
        )
