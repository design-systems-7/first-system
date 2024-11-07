from app.models.base_class import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
import uuid


class OrderStatus(enum.Enum):
    active = "active"
    taken = "taken"
    cancelled = "cancelled"
    done = "done"


class Order(Base):
    assigned_order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4, index=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.active)
    price = Column(Float, nullable=False)
    executor_id = Column(Integer, nullable=True, index=True)
    zone = Column(String, nullable=False)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    taken_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
