import uuid
from typing import Optional, Any

from app.schemas.order import AssignedOrder
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.core.issue_order_service.issue_order_service import issue_order_service

from app.app_logger import logger

router = APIRouter()


@router.post("/issue_order", status_code=status.HTTP_200_OK, response_model=AssignedOrder)
async def handle_issue_order(executer_id: uuid.UUID, last_taken_order_id: Optional[uuid.UUID] = None,
                             session: AsyncSession = Depends(get_db)) -> Any:
    try:
        new_order = await issue_order_service.issue_order_for_execution(
            session=session,
            executer_id=executer_id,
            last_taken_order_id=last_taken_order_id
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to issue an order")

    if not new_order:
        await session.commit()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active orders")
    return new_order


@router.post("/check_order_for_updates", status_code=status.HTTP_200_OK, response_model=AssignedOrder)
async def check_order_for_updates(order_id: uuid.UUID,
                                  session: AsyncSession = Depends(get_db)) -> Any:
    try:
        updated_order = await issue_order_service.issue_order_for_update_check(
            session=session,
            order_id=order_id
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to issue an updated order")

    if not updated_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issued order not found")
    return updated_order
