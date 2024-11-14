import asyncio
import logging

from sqlalchemy import Engine, select
from sqlalchemy.engine import Connection
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.database.db import engine
from app.tasks import update_config_cache_task
from app.core.config import settings

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


async def run_periodic_task(periodic_task: callable, seconds: int) -> None:
    while True:
        await asyncio.wait_for(periodic_task(), timeout=None)
        await asyncio.sleep(seconds)


def run_scheduler() -> None:
    loop = asyncio.new_event_loop()
    task = loop.create_task(run_periodic_task(update_config_cache_task, settings.CONFIGS_CACHE_UPDATE_EVERY_SECONDS))

    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(db_health_check(engine))
    run_scheduler()
