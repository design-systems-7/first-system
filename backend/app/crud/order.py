from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.order import Order, OrderStatus
from datetime import datetime, timedelta
from typing import Optional
from app.core.cancel_order.py import can_cancel_order
from app.core.complete_order.py import can_complete_order


class DatabaseAdapter:

    async def write_order(self, session: AsyncSession, order_data: dict) -> Order:
        new_order = Order(**order_data)
        session.add(new_order)
        await session.commit()
        await session.refresh(new_order)
        return new_order

    async def get_active_order(self, session: AsyncSession, executor_id: int) -> Optional[Order]:
        # 2 query
        # 1 select + 1 update
        query = select(Order).where(Order.executor_id == executor_id, Order.status == OrderStatus.active)
        result = await session.execute(query)
        order = result.scalar_one_or_none()

        if order:
            order.status = OrderStatus.taken
            await session.commit()
            await session.refresh(order)
        return order

    async def cancel_order(self, session: AsyncSession, order_id: int, executor_id: int) -> Optional[Order]:
        query = select(Order).where(Order.order_id == order_id, Order.executor_id == executor_id)
        result = await session.execute(query)
        order = result.scalar_one_or_none()

        if order and can_cancel_order(order):
            stmt = (
                update(Order)
                .where(Order.order_id == order_id, Order.executor_id == executor_id)
                .values(status=OrderStatus.cancelled)
                .returning(Order)
            )
            result = await session.execute(stmt)
            order = result.scalar_one_or_none()
            return order

        return None

    async def complete_order(self, session: AsyncSession, order_id: int, executor_id: int) -> Optional[Order]:
        query = select(Order).where(Order.order_id == order_id, Order.executor_id == executor_id)
        result = await session.execute(query)
        order = result.scalar_one_or_none()

        if order and can_complete_order(order):
            stmt = (
                update(Order)
                .where(Order.order_id == order_id, Order.executor_id == executor_id)
                .values(status=OrderStatus.done)
                .returning(Order)
            )
            result = await session.execute(stmt)
            order = result.scalar_one_or_none()
            return order

        return None
