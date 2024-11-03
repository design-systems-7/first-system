from app.models.base_class import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, JSON
from datetime import datetime
import enum


class OrderStatus(enum.Enum):
    active = "active"
    taken = "taken"
    cancelled = "cancelled"
    done = "done"


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {'extend_existing': True}

    order_id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.active)
    price = Column(Float, nullable=False)
    executor_id = Column(Integer, nullable=True, index=True)
    zone = Column(String, nullable=False)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
