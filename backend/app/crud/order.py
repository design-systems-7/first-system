from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app.models.order import Order, OrderStatus
from datetime import datetime
from typing import Optional
import uuid

from app.schemas.order import AssignedOrder


class CRUDOrder:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def add_order(self, order_data: AssignedOrder) -> Order:
        new_order = Order(**asdict(order_data))
        self.async_session.add(new_order)
        return new_order

    async def cancel_active_order_within_safety_time(self,
                                                     assigned_order_id: uuid.UUID,
                                                     safety_datetime: datetime) -> Optional[Order]:
        query = (
            update(Order)
            .where(Order.assigned_order_id == assigned_order_id,
                   Order.status.in_([OrderStatus.active, OrderStatus.cancelled]),
                   Order.assign_time > safety_datetime)
            .values(status=OrderStatus.cancelled)
            .returning(Order)
        )
        result = await self.async_session.execute(query)
        order = result.scalar_one_or_none()
        return order
