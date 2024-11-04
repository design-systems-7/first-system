from fastapi import APIRouter

from app.core.assign_order_service.assign_order_service import AssignOrderService
from app.core.assign_order_service.data_provider import DataProvider
from app.core.assign_order_service.payment_calculator import PaymentCalculator
from app.core.assign_order_service.route_information_provider import RouteInformationProvider
from app.crud.order import DatabaseAdapter

router = APIRouter()

service = AssignOrderService(
    DataProvider(),
    PaymentCalculator(),
    RouteInformationProvider(),
    DatabaseAdapter()
)


@router.post("/assign_order", status_code=201)
async def handle_assign_order(order_id: str, executer_id: str, locale: str) -> None:
    await service.handle_assign_order(order_id, executer_id, locale)
    # TODO возвращать статусы


@router.get("/update_config_cache")
async def update_config_cache() -> None:
    await service.data_provider.update_config_cache()
