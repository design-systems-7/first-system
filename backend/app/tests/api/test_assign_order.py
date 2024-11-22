import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from httpx import AsyncClient, TimeoutException

import pytest_asyncio
import uuid

from app.main import app
from app.core.config import settings


def test_assign_order_endpoint(
        client: TestClient
):
    test_order_id = uuid.uuid4()
    test_executor_id = uuid.uuid4()

    try:
        response = client.post(
            f"{settings.API_V1_STR}/assign_order",
            params={
                "order_id": test_order_id,
                "executer_id": test_executor_id,
                "locale": "en"
            }
        )

        assert (response.status_code == 201)
        data = response.json()
        assert "assigned_order_id" in data
        assert data["order_id"] == str(test_order_id)
        assert data["executer_id"] == str(test_executor_id)

    except TimeoutException:
        pytest.fail("Test timed out while waiting for response")
    except Exception as e:
        pytest.fail(f"Test failed with exception: {str(e)}")
