from datetime import datetime, timedelta
from app.database import DatabaseAdapter
from sqlalchemy.ext.asyncio import AsyncSession
import uuid


async def cancel_order(
        db_adapter: DatabaseAdapter,
        session: AsyncSession,
        assigned_order_id: uuid.UUID,
        safety_period_minutes: int
):
    safety_datetime = datetime.utcnow() - timedelta(minutes=safety_period_minutes)

    cancelled_order = await db_adapter.cancel_active_order_within_safety_time(
        session=session,
        assigned_order_id=assigned_order_id,
        safety_datetime=safety_datetime
    )

    # if cancelled_order:
    #     print(f"Order {assigned_order_id} was cancelled.")
    # else:
    #     print(f"Order {assigned_order_id} could not be cancelled within the safety period.")

    return cancelled_order
