from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.order import Order, OrderStatus
from datetime import datetime
from typing import Optional
import uuid


class DatabaseAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def add_order(self, session: AsyncSession, order_data: dict) -> Order:
        new_order = Order(**order_data)
        self.async_session.add(new_order)
        return new_order

    async def cancel_active_order_within_safety_time(self,
                                                     session: AsyncSession,
                                                     assigned_order_id: uuid.UUID,
                                                     safety_datetime: datetime) -> Optional[Order]:
        query = (
            update(Order)
            .where(Order.assigned_order_id == assigned_order_id,
                   Order.status == OrderStatus.active,
                   Order.assign_time > safety_datetime)
            .values(status=OrderStatus.cancelled)
            .returning(Order)
        )
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        return order
