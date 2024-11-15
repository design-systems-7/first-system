import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .data_provider import DataProvider
from app.crud.order import CRUDOrder
from app.schemas.order import AssignedOrder
from app.models.order import Order
from .payment_calculator import PaymentCalculator
from .route_information_provider import RouteInformationProvider


class AssignOrderService:

    SAFETY_TIMEDELTA_IN_MINUTES = 10

    def __init__(self,
                 data_provider: DataProvider,
                 payment_calculator: PaymentCalculator,
                 route_info_provider: RouteInformationProvider):
        self.data_provider = data_provider
        self.payment_calculator = payment_calculator
        self.route_info_provider = route_info_provider

    async def handle_assign_order(self, session: AsyncSession, order_id: str, executer_id: str, locale: str):
        order_data, zone_info, executer_profile, configs, tolls_data = await self.data_provider.collect_order_info(
            order_id,
            executer_id)

        final_coin_amount = self.payment_calculator.calculate_payment(order_data, zone_info, configs, tolls_data)

        route_information = self.route_info_provider.get_route_info(executer_profile, zone_info)

        order = AssignedOrder(
            assign_order_id=str(uuid.uuid4()),
            order_id=order_id,
            executer_id=executer_id,
            final_coin_amount=final_coin_amount,
            route_information=route_information,
            assign_time=datetime.now(),
            acquire_time=None,
        )

        crud_order: CRUDOrder = CRUDOrder(session)
        new_order = await crud_order.add_order(order_data=order)
        return new_order

    async def handle_cancel_order(self, session: AsyncSession, assigned_order_id: uuid.UUID) -> Optional[Order]:
        safety_datetime = datetime.utcnow() - timedelta(minutes=self.SAFETY_TIMEDELTA_IN_MINUTES)

        crud_order: CRUDOrder = CRUDOrder(session)
        cancelled_order = await crud_order.cancel_active_order_within_safety_time(
            session=session,
            assigned_order_id=assigned_order_id,
            safety_datetime=safety_datetime
        )

        return cancelled_order


service = AssignOrderService(
    DataProvider(),
    PaymentCalculator(),
    RouteInformationProvider()
)
