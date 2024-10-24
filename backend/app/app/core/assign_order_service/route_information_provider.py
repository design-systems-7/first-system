from models.models import ExecuterProfile, ZoneData


class RouteInformationProvider:
    """A class that provides route information required for an order."""

    MAGIC_CONSTANT = 8

    def get_route_info(self, executer_profile: ExecuterProfile, zone_info: ZoneData) -> str:
        if executer_profile.rating >= self.MAGIC_CONSTANT:
            return f'Order at zone "{zone_info.display_name}"'

        return 'Order at somewhere'
