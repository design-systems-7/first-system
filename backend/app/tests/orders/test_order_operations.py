# first-system/backend/app/tests/test_order_operations.py

import pytest
import uuid
from datetime import datetime, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.database.db import get_db
from app.models.order import Order, OrderStatus
from app.database.db import AsyncSessionLocal
from app.models.order import OrderStatus

import pytest
import uuid
from datetime import datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.config import settings
from app.models.order import Order, OrderStatus
from app.database.db import AsyncSessionLocal
from app.core.assign_order_service.assign_order_service import service



# @pytest.mark.asyncio
# async def test_assign_order_saves_to_db():
#     test_order_id = str(uuid.uuid4())
#     test_executer_id = "test-executer"

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.post(
#             f"{settings.API_V1_STR}/assign_order",
#             params={
#                 "order_id": test_order_id,
#                 "executer_id": test_executer_id,
#                 "locale": "en"
#             }
#         )

#     assert response.status_code == 201, f"Unexpected status code: {response.status_code}"
#     data = response.json()
#     assigned_order_id = data["assigned_order_id"]

#     async with AsyncSessionLocal() as session:
#         order = await session.get(Order, uuid.UUID(assigned_order_id))
#         assert order is not None, "Order not found in database"
#         assert str(order.order_id) == test_order_id
#         assert order.executer_id == test_executer_id
#         assert order.status == OrderStatus.active

def test_cancel_order_updates_db(client: TestClient):
    test_order_id = uuid.uuid4()
    test_executer_id = uuid.uuid4()

    assign_response = client.post(
        f"{settings.API_V1_STR}/assign_order",
        params={
            "order_id": test_order_id,
            "executer_id": test_executer_id,
            "locale": "en"
        }
    )

    assert assign_response.status_code == 201, f"Unexpected status code: {assign_response.status_code}"
    assign_data = assign_response.json()
    assigned_order_id = assign_data["assigned_order_id"]

    cancel_response = client.post(
        f"{settings.API_V1_STR}/cancel_order",
        params={
            "assigned_order_id": assigned_order_id
        }
    )

    assert cancel_response.status_code == 200, f"Unexpected status code: {cancel_response.status_code}"
    cancel_data = cancel_response.json()
    assert cancel_data["assigned_order_id"] == assigned_order_id
