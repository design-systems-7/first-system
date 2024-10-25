from typing import Tuple
from app.schemas.order import OrderData, ZoneData, ConfigMap, ExecuterProfile


# TODO разбить
class PaymentCalculator:
    """A class that handles the price calculation for an order."""

    def calculate_payment(self,
                          order_data: OrderData,
                          zone_info: ZoneData,
                          configs: ConfigMap) -> float:
        pass


class DataProvider:
    """A class that asynchronously fetches data needed to create an order from multiple data sources at once."""

    def fetch_order_info(self, order_id: str, executer_id: str) -> Tuple[
        OrderData, ZoneData, ExecuterProfile, ConfigMap
    ]:
        return None, None, None, None


class RouteInformationProvider:
    """A class that provides route information required for an order."""

    def get_route_info(self, executer_profile: ExecuterProfile) -> str:
        pass
