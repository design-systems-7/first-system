import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from httpx import AsyncClient, TimeoutException

import pytest_asyncio
import uuid

from app.main import app
from app.core.config import settings

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"{settings.API_V1_STR}/utils/health-check/")
    assert response.status_code == 200
    assert response.json() is True






@pytest.mark.asyncio
async def test_assign_order_endpoint():
    test_order_id = str(uuid.uuid4())
    test_executor_id = "test-executor"
    
    async with AsyncClient(app=app, base_url="http://test", timeout=10.0) as ac:
        try:
            response = await ac.post(
                f"{settings.API_V1_STR}/assign_order",
                params={
                    "order_id": test_order_id,
                    "executer_id": test_executor_id,
                    "locale": "en"
                }
            )
            
            
            assert(response.status_code == 201)
            data = response.json()
            assert "assigned_order_id" in data
            assert data["order_id"] == test_order_id
            assert data["executer_id"] == test_executor_id
            
        except TimeoutException:
            pytest.fail("Test timed out while waiting for response")
        except Exception as e:
            pytest.fail(f"Test failed with exception: {str(e)}")
