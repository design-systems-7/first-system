from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.order import Order, OrderStatus
from datetime import datetime, timedelta
from typing import Optional


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
        # TODO 2 query
        # 1 select + 1 update
        query = select(Order).where(Order.order_id == order_id, Order.executor_id == executor_id)
        result = await session.execute(query)
        order = result.scalar_one_or_none()

        # TODO вынести проверки бизнес-уровня на бизнес-уровень (core)
        if order and order.status == OrderStatus.active and order.created_at + timedelta(
                minutes=10) > datetime.utcnow():
            order.status = OrderStatus.cancelled
            await session.commit()
            await session.refresh(order)
        return order

    async def complete_order(self, session: AsyncSession, order_id: int, executor_id: int) -> Optional[Order]:
        # TODO 2 query
        # 1 select + 1 update
        query = select(Order).where(Order.order_id == order_id, Order.executor_id == executor_id)
        result = await session.execute(query)
        order = result.scalar_one_or_none()

        # TODO вынести проверки бизнес-уровня на бизнес-уровень (core)
        if order and order.status == OrderStatus.taken:
            order.status = OrderStatus.done
            await session.commit()
            await session.refresh(order)
        return order
