import uuid
from dataclasses import dataclass

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.order import Order


@dataclass
class AssignedOrder:
    assign_order_id: uuid.UUID
    order_id: uuid.UUID
    executer_id: str
    coin_coeff: float
    coin_bonus_amount: float
    final_coin_amount: float
    route_information: str

    # audit fields
    assign_time: datetime
    acquire_time: datetime


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
