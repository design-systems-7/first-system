from datetime import datetime

import pytest

from app.crud.order import CRUDOrder
from app.database.db import AsyncSessionLocal
from app.models.order import OrderStatus


@pytest.mark.asyncio
async def test_write_order():
    async with AsyncSessionLocal() as session:
        adapter = CRUDOrder(session)
        order_data = {
            "status": OrderStatus.active,
            "price": 100.0,
            "zone": "A1",
            "created_at": datetime.utcnow(),
        }
        new_order = await adapter.add_order(order_data)
        assert new_order is not None
        assert new_order.status == OrderStatus.active
        assert new_order.price == 100.0
        assert new_order.zone == "A1"

# @pytest.mark.asyncio
# async def test_get_active_order():
#     async with AsyncSessionLocal() as session:
#         adapter = CRUDOrder()
#         order_data = {
#             "status": OrderStatus.active,
#             "price": 200.0,
#             "zone": "B2",
#             "created_at": datetime.utcnow(),
#         }
#         new_order = await adapter.write_order(session, order_data)
#
#         active_order = await adapter.get_active_order(session, new_order.order_id, executor_id=1)
#         assert active_order is not None
#         assert active_order.status == OrderStatus.taken
#         assert active_order.executor_id == 1
#
#
# @pytest.mark.asyncio
# async def test_cancel_order():
#     async with AsyncSessionLocal() as session:
#         adapter = CRUDOrder()
#         order_data = {
#             "status": OrderStatus.active,
#             "price": 300.0,
#             "zone": "C3",
#             "created_at": datetime.utcnow(),
#         }
#         new_order = await adapter.write_order(session, order_data)
#
#         cancelled_order = await adapter.cancel_order(session, new_order.order_id, executor_id=None)
#         assert cancelled_order is not None
#         assert cancelled_order.status == OrderStatus.cancelled
#
#
# @pytest.mark.asyncio
# async def test_complete_order():
#     async with AsyncSessionLocal() as session:
#         adapter = CRUDOrder()
#         order_data = {
#             "status": OrderStatus.taken,
#             "price": 400.0,
#             "zone": "D4",
#             "created_at": datetime.utcnow(),
#             "executor_id": 2,
#         }
#         new_order = await adapter.write_order(session, order_data)
#
#         completed_order = await adapter.complete_order(session, new_order.order_id, executor_id=2)
#         assert completed_order is not None
#         assert completed_order.status == OrderStatus.done
