import uuid
from datetime import datetime

from fastapi import APIRouter

from app.crud.order import DatabaseAdapter
from app.schemas.order import AssignedOrder
from app.core.assign_order import DataProvider, PaymentCalculator, RouteInformationProvider

router = APIRouter()


# прописать нормально!
@router.post("/assign_order", status_code=201)
def handle_assign_order(order_id: str, executer_id: str, locale: str) -> None:
    order_data, zone_info, executer_profile, configs = DataProvider().fetch_order_info(order_id, executer_id)
    final_coin_amount = PaymentCalculator().calculate_payment(order_data, zone_info, configs)
    route_information = RouteInformationProvider().get_route_info(executer_profile)
    order = AssignedOrder(
        assign_order_id=str(uuid.uuid4()),
        order_id=order_id,
        executer_id=executer_id,
        final_coin_amount=final_coin_amount,
        route_information=route_information,
        assign_time=datetime.now(),
        acquire_time=None,
    )
    DatabaseAdapter().write_order(order)
    # TODO возвращать статусы
