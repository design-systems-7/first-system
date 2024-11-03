from app.models.order import Order, OrderStatus


def can_complete_order(order: Order) -> bool:
    return order.status == OrderStatus.taken
