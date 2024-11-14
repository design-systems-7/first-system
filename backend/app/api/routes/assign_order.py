from fastapi import APIRouter

from app.core.config import settings
from app.core.assign_order_service.assign_order_service import AssignOrderService
from app.core.assign_order_service.data_provider import DataProvider
from app.core.assign_order_service.payment_calculator import PaymentCalculator
from app.core.assign_order_service.route_information_provider import RouteInformationProvider
from app.crud.order import DatabaseAdapter

router = APIRouter()

# TODO переместил бы куда-то в base в core -- логически там хочется
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


@router.get("/reload_config")
async def reload_config() -> None:
    settings.__init__()
