from dataclasses import dataclass

from datetime import datetime
from typing import Optional


@dataclass
class OrderData:
    id: str
    user_id: str
    zone_id: str
    base_coin_amount: float


@dataclass
class ZoneData:
    id: str
    coin_coeff: float
    display_name: str


@dataclass
class ExecuterProfile:
    id: str
    tags: list[str]
    rating: float


@dataclass
class AssignedOrder:
    assign_order_id: str
    order_id: str
    executer_id: str
    final_coin_amount: float
    route_information: str

    # audit fields
    assign_time: datetime
    acquire_time: Optional[datetime]


class ConfigMap:
    def __init__(self, data: dict):
        self._data = data
        for k, v in data.items():
            self.__setattr__(k, v)

    def __getattr__(self, item):
        return self._data.get(item, None)


@dataclass
class TollRoadsData:
    bonus_amount: float
