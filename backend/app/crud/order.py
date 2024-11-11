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

    async def get_order_by_id(self, session: AsyncSession, assigned_order_id: uuid.UUID) -> Optional[Order]:
        query = select(Order).where(Order.assigned_order_id == assigned_order_id)
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        return order

    async def update_order_status(self, session: AsyncSession, assigned_order_id: uuid.UUID, new_status: OrderStatus) -> Optional[Order]:
        query = (
            update(Order)
            .where(Order.assigned_order_id == assigned_order_id)
            .values(status=new_status)
            .returning(Order)
        )
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        return order
