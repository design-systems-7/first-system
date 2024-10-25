import uuid
from datetime import datetime

from data_provider import DataProvider
from database.database_adapter import DatabaseAdapter
from models.models import AssignedOrder
from payment_calculator import PaymentCalculator
from route_information_provider import RouteInformationProvider


class AssignOrderService:
    def __init__(self,
                 data_provider: DataProvider,
                 payment_calculator: PaymentCalculator,
                 route_info_provider: RouteInformationProvider,
                 database_adapter: DatabaseAdapter):
        self.data_provider = data_provider
        self.payment_calculator = payment_calculator
        self.route_info_provider = route_info_provider
        self.database_adapter = database_adapter

    async def handle_assign_order(self, order_id: str, executer_id: str, locale: str):
        order_data, zone_info, executer_profile, configs, tolls_data = await self.data_provider.fetch_order_info(order_id,
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

        self.database_adapter.write_order(order)
