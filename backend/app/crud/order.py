from app.schemas.order import AssignedOrder


# TODO тут можно переименовать в DatabaseOrder
class DatabaseAdapter:
    """A class that manages interactions with the database."""

    def write_order(self, order: AssignedOrder):
        pass
