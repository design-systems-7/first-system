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
