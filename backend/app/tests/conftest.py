from collections.abc import Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.main import app
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete

from app.models.order import Order

from app.database.db import engine, AsyncSessionLocal


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db() -> Generator[AsyncSession, None, None]:
    async with AsyncSessionLocal() as session:
        yield session
        statement = delete(Order)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c
