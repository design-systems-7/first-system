from os import environ
from typing import Tuple
from urllib.parse import urlencode

import aiohttp
import asyncio

from models.models import OrderData, ZoneData, ExecuterProfile, ConfigMap, TollRoadsData


class DataProvider:
    """A class that asynchronously fetches data needed to create an order from multiple data sources at once."""

    async def fetch_order_info(self, order_id: str, executer_id: str) -> Tuple[
        OrderData, ZoneData, ExecuterProfile, ConfigMap, TollRoadsData
    ]:
        async with aiohttp.ClientSession() as session:
            order_data_task = self.get_order_data(session, order_id)
            executer_profile_task = self.get_executer_profile(session, executer_id)
            configs_task = self.get_configs(session)

            order_data, executer_profile, configs = await asyncio.gather(
                order_data_task, executer_profile_task, configs_task
            )

            zone_data = await self.get_zone_data(session, order_data.zone_id)

            toll_roads_data = await self.get_toll_roads(session, zone_data.display_name)

            return order_data, zone_data, executer_profile, configs, toll_roads_data

    async def get_order_data(self, session: aiohttp.ClientSession, order_id: str) -> OrderData:
        url = environ.get('order_data_endpoint') + urlencode({'id': order_id})
        async with session.get(url) as response:
            response_data = await response.json()
            return OrderData(
                id=order_id,
                zone_id=response_data['zone_id'],
                user_id=response_data['user_id'],
                base_coin_amount=response_data['base_coin_amount']
            )

    async def get_zone_data(self, session: aiohttp.ClientSession, zone_id: str) -> ZoneData:
        url = environ.get('zone_data_endpoint') + urlencode({'id': zone_id})
        async with session.get(url) as response:
            response_data = await response.json()
            return ZoneData(
                id=zone_id,
                coin_coeff=response_data['coin_coeff'],
                display_name=response_data['display_name']
            )

    async def get_executer_profile(self, session: aiohttp.ClientSession, executer_id: str) -> ExecuterProfile:
        url = environ.get('executer_profile_endpoint') + urlencode({'id': executer_id})
        async with session.get(url) as response:
            response_data = await response.json()
            return ExecuterProfile(
                id=executer_id,
                tags=response_data['tags'],
                rating=response_data['rating']
            )

    async def get_configs(self, session: aiohttp.ClientSession) -> ConfigMap:
        url = environ.get('configs_endpoint')
        async with session.get(url) as response:
            return ConfigMap(await response.json())

    async def get_toll_roads(self, session: aiohttp.ClientSession, zone_display_name: str) -> TollRoadsData:
        url = environ.get('tollroads_endpoint') + urlencode({'zone_display_name': zone_display_name})
        async with session.get(url) as response:
            response_data = await response.json()
            return TollRoadsData(
                response_data['bonus_amount']
            )
