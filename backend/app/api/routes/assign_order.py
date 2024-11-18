import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.assign_order_service.assign_order_service import service
from app.core.config import settings
from app.database.db import get_db
from app.schemas.order import AssignedOrder
import traceback
import logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/assign_order", status_code=201, response_model=AssignedOrder)
async def handle_assign_order(order_id: uuid.UUID, executer_id: uuid.UUID, locale: str,
                              session: AsyncSession = Depends(get_db)) -> Optional[AssignedOrder]:
    try:
        return await service.handle_assign_order(session=session,
                                                 order_id=order_id, executer_id=executer_id, locale=locale)
    except Exception as e:
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
        logger.error(f"Failed to assign order: {e}\n{traceback_str}")
        raise HTTPException(status_code=500, detail=f"Failed to assign order: {str(e)}")
        # raise HTTPException(status_code=500, detail=f"Failed to assign order: {str(e)}")


@router.post("/cancel_order", status_code=200, response_model=AssignedOrder)
async def handle_cancel_order(assigned_order_id: uuid.UUID,
                              session: AsyncSession = Depends(get_db)) -> Optional[AssignedOrder]:
    try:
        cancelled_order = await service.handle_cancel_order(session=session,
                                                            assigned_order_id=assigned_order_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")

    if cancelled_order is None:
        raise HTTPException(status_code=404, detail="Order does not exist or cannot be cancelled")

    return cancelled_order


@router.get("/reload_config")
async def reload_config() -> None:
    settings.__init__()
