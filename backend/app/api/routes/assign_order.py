import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.core.assign_order_service.assign_order_service import AssignOrderService
from app.core.assign_order_service.data_provider import DataProvider
from app.core.assign_order_service.payment_calculator import PaymentCalculator
from app.core.assign_order_service.route_information_provider import RouteInformationProvider
from app.database.db import get_db
from app.schemas.order import AssignedOrder
from app.crud.order import DatabaseAdapter
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()

# TODO переместил бы куда-то в base в core -- логически там хочется
service = AssignOrderService(
    DataProvider(),
    PaymentCalculator(),
    RouteInformationProvider(),
    DatabaseAdapter()
)


# todo коды еще можно тоже переделать на константы

@router.post("/assign_order", status_code=201)
async def handle_assign_order(order_id: str, executer_id: str, locale: str) -> None:
    await service.handle_assign_order(order_id, executer_id, locale)
    # TODO возвращать статусы


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
