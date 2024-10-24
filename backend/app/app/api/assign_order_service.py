from fastapi import APIRouter

from core.assign_order_service.assign_order_service import AssignOrderService
from core.assign_order_service.data_provider import DataProvider
from database.database_adapter import DatabaseAdapter
from core.assign_order_service.route_information_provider import RouteInformationProvider
from core.assign_order_service.payment_calculator import PaymentCalculator

assign_order_service_router = APIRouter()

service = AssignOrderService(
    DataProvider(),
    PaymentCalculator(),
    RouteInformationProvider(),
    DatabaseAdapter()
)



@assign_order_service_router.put('/assign')
async def assign_order(order_id: str, executer_id: str, locale: str = 'en_US'):
    await service.handle_assign_order(order_id, executer_id, locale)