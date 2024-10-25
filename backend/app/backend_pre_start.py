import asyncio
import logging

from sqlalchemy import Engine, select
from sqlalchemy.engine import Connection
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.database.db import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


def select_test(conn: Connection) -> None:
    conn.execute(
        select(1)
    )


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def db_health_check(db_engine: Engine) -> None:
    try:
        async with db_engine.begin() as conn:
            await conn.run_sync(select_test)
    except Exception as e:
        logger.error(e)
        raise e


async def main() -> None:
    await db_health_check(engine)


if __name__ == "__main__":
    asyncio.run(main())
