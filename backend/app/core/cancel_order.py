from datetime import datetime, timedelta
from app.models.order import Order, OrderStatus


def can_cancel_order(order: Order) -> bool:
    return (
            order.status == OrderStatus.active and
            order.created_at + timedelta(minutes=10) > datetime.utcnow()
    )
