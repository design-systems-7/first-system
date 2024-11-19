import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.order import OrderCRUD


class CompleteOrderService:
    """A class for marking order as complete (more generally - changing its status)"""

    async def mark_order_as_complete(self, session: AsyncSession, assigned_order_id: Optional[uuid.UUID]) -> None:
        if assigned_order_id:
            await OrderCRUD(session).mark_order_as_completed(assigned_order_id=assigned_order_id)
