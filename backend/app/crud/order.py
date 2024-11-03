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

    async def get_taken_order(self, session: AsyncSession, executor_id: int) -> Optional[Order]:
        query = (
                Order.select()
                .where(Order.executor_id == executor_id, Order.status == OrderStatus.taken)
        )
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        return order

    async def get_active_orders_for_execution(self, session: AsyncSession, executor_id: int) -> List[Order]:
        query = (
            select(Order)
            .where(Order.executor_id == executor_id, Order.status == OrderStatus.active)
        )
        result = await session.execute(query)
        orders = result.scalars().all()
        return orders

    async def take_order(self, session: AsyncSession, order_id: int) -> Optional[Order]:
        query = (
            update(Order)
            .where(Order.order_id == order_id, Order.status == OrderStatus.active)
            .values(status=OrderStatus.taken)
            .returning(Order)
        )
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        return order

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

    async def complete_order(self, session: AsyncSession, order_id: int) -> Optional[Order]:
        query = (
                Order.update()
                .where(Order.order_id == order_id)
                .values(status=OrderStatus.done)
                .returning(Order)
        )
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        return order
