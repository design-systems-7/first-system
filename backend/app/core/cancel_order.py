from datetime import datetime, timedelta
from app.crud.order import DatabaseAdapter
from sqlalchemy.ext.asyncio import AsyncSession
import uuid


class CancellationService:
    def __init__(self, db_adapter: DatabaseAdapter):
        self.db_adapter = db_adapter

    async def cancel_order(self, session: AsyncSession, assigned_order_id: uuid.UUID):
        safety_datetime = datetime.utcnow() - timedelta(minutes=10)

        cancelled_order = await self.db_adapter.cancel_active_order_within_safety_time(
            session=session,
            assigned_order_id=assigned_order_id,
            safety_datetime=safety_datetime
        )

        return cancelled_order