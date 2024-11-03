from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.order import Order, OrderStatus
from datetime import datetime, timedelta
from typing import List, Optional


class DatabaseAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def add_order(self, session: AsyncSession, order_data: dict) -> Order:
        new_order = Order(**order_data)
        self.async_session.add(new_order)
        return new_order

    async def cancel_active_order_within_safety_time(self,
                                                     session: AsyncSession,
                                                     order_id: int,
                                                     safety_datetime: datetime.datetime) -> Optional[Order]:
        query = (
                Order.update()
                .where(Order.order_id == order_id,
                       Order.status == OrderStatus.active,
                       Order.created_at > safety_datetime)
                .values(status=OrderStatus.cancelled)
                .returning(Order)
        )
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        return order
