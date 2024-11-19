from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.order import Order, OrderStatus
import datetime as dt
from typing import Optional
import uuid


class OrderCRUD:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def check_for_issued_order(self, executer_id: uuid.UUID) -> Optional[Order]:
        query = (
            select(Order)
            .where(Order.executer_id == executer_id, Order.status == OrderStatus.taken)
        )
        result = await self.async_session.execute(query)
        # В любой момент времени у любого исполнителя может быть выдан максимум один заказ
        order = result.scalars().one_or_none()
        return order

    async def get_issued_order(self, assigned_order_id: uuid.UUID) -> Optional[Order]:
        query = (
            select(Order)
            .where(Order.assigned_order_id == assigned_order_id, Order.status == OrderStatus.taken)
        )
        result = await self.async_session.execute(query)
        order = result.scalars().one_or_none()
        return order

    async def get_active_order_for_execution(self,
                                             executer_id: uuid.UUID) -> Optional[Order]:
        query = (
            select(Order)
            .with_for_update()
            .where(Order.executer_id == executer_id, Order.status == OrderStatus.active)
        )
        result = await self.async_session.execute(query)
        order = result.scalars().first()
        return order

    async def take_order(self,
                         assigned_order_id: uuid.UUID, acquire_time: dt.datetime) -> Optional[Order]:
        query = (
            update(Order)
            .where(Order.assigned_order_id == assigned_order_id, Order.status == OrderStatus.active)
            .values(status=OrderStatus.taken, acquire_time=acquire_time)
            .returning(Order)
        )
        result = await self.async_session.execute(query)
        order = result.scalars().one_or_none()
        return order

    async def mark_order_as_completed(self, assigned_order_id: uuid.UUID) -> Optional[Order]:
        query = (
            update(Order)
            .where(Order.assigned_order_id == assigned_order_id)
            .values(status=OrderStatus.done)
            .returning(Order)
        )
        result = await self.async_session.execute(query)
        order = result.scalars().one_or_none()
        return order
