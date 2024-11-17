from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.models.order import Order


# TODO разбить
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
    assigned_order_id: str
    order_id: str
    executer_id: str
    coin_coeff: float
    coin_bonus_amount: float
    final_coin_amount: float
    route_information: str

    # audit fields
    assign_time: datetime
    acquire_time: Optional[datetime]


def assigned_order_from_order(order: Order) -> AssignedOrder:
    return AssignedOrder(
        order.assigned_order_id,
        order.order_id,
        order.executer_id,
        order.coin_coeff,
        order.coin_bonus_amount,
        order.final_coin_amount,
        order.route_information,
        order.assign_time,
        order.acquire_time,
    )


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
