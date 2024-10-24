from typing import AsyncIterator

from app.database.session import AsyncSessionLocal
from sqlalchemy.orm import sessionmaker


# https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#a-database-dependency-with-yield
async def get_db() -> AsyncIterator[sessionmaker]:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session
