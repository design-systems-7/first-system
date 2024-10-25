from models.models import OrderData, ZoneData, ConfigMap, TollRoadsData


class PaymentCalculator:
    """A class that handles the price calculation for an order."""

    def calculate_payment(self,
                          order_data: OrderData,
                          zone_info: ZoneData,
                          configs: ConfigMap,
                          tolls_data: TollRoadsData) -> float:
        actual_coin_coeff = zone_info.coin_coeff
        if configs.coin_coeff_settings is not None:
            actual_coin_coeff = min(float(configs.coin_coeff_settings['maximum']), actual_coin_coeff)
        final_coin_amount = order_data.base_coin_amount * actual_coin_coeff + tolls_data.bonus_amount
        return final_coin_amount
