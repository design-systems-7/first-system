from datetime import datetime, timedelta
from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.order import DatabaseAdapter
from app.models.order import Order, OrderStatus


class OrderCancellationService:
    def __init__(self, db_adapter: DatabaseAdapter):
        self.db_adapter = db_adapter

    async def cancel_order(self, session: AsyncSession, assigned_order_id: uuid.UUID, max_cancel_duration: timedelta) -> \
    Optional[Order]:
        order = await self.db_adapter.get_order_by_id(session, assigned_order_id)

        if not order or order.status != OrderStatus.active:
            return None

        current_time = datetime.utcnow()
        safety_time = order.assign_time + max_cancel_duration
        if current_time > safety_time:
            return None

        cancelled_order = await self.db_adapter.update_order_status(
            session=session,
            assigned_order_id=assigned_order_id,
            new_status=OrderStatus.cancelled
        )
        return cancelled_order
