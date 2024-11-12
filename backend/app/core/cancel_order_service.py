import uuid
from app.crud.order import DatabaseAdapter
from app.schemas.order import AssignedOrder
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


class CancelOrderService:
    """A class for marking order as cancelled (more generally - changing its status)"""

    async def mark_order_as_cancelled(self, session: AsyncSession,
                                      assigned_order_id: uuid.UUID) -> Optional[AssignedOrder]:
        crud_order: DatabaseAdapter = DatabaseAdapter(session)
        safety_datetime = datetime.utcnow() - timedelta(minutes=10)

        cancelled_order = await crud_order.cancel_active_order_within_safety_time(
            session=session,
            assigned_order_id=assigned_order_id,
            safety_datetime=safety_datetime
        )

        return AssignedOrder.from_orm(cancelled_order)


cancel_order_service = CancelOrderService()
