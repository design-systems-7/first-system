import uuid
from typing import Optional

from app.core.cancel_order_service import cancel_order_service
from app.database.db import get_db
from app.schemas.order import AssignedOrder
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/cancel_order", status_code=200, response_model=AssignedOrder)
async def cancel_order(assigned_order_id: uuid.UUID,
                       session: AsyncSession = Depends(get_db)) -> Optional[AssignedOrder]:
    try:
        cancelled_order = await cancel_order_service.mark_order_as_cancelled(session=session,
                                                                             assigned_order_id=assigned_order_id)

        if cancelled_order is None:
            raise HTTPException(status_code=404, detail="Order cannot be cancelled")
        return cancelled_order

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")
