import datetime as dt
import enum
import uuid

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_class import Base
from sqlalchemy.sql import func

class OrderStatus(enum.Enum):
    active = "active"
    taken = "taken"
    cancelled = "cancelled"
    done = "done"


class Order(Base):
    assigned_order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.UUID)
    modified_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
    order_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    executer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.active)
    coin_coeff = Column(Float, nullable=False)
    coin_bonus_amount = Column(Float, nullable=False)
    final_coin_amount = Column(Float, nullable=False)
    route_information = Column(String, nullable=False)
    assign_time = Column(DateTime, default=dt.datetime.utcnow, nullable=False)
    acquire_time = Column(DateTime, nullable=True)
