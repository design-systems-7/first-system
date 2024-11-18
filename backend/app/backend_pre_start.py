import asyncio
import logging
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy import Engine, select
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.config import settings
from app.database.db import engine
from app.tasks import update_config_cache_task, close_redis_connection
from app.app_logger import logger

max_tries = 60  # 1 minute
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


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def redis_health_check() -> None:
    try:
        redis_client = Redis(host='redis_cache', port=6379, socket_connect_timeout=1)
        redis_client.ping()
    except RedisConnectionError as e:
        logger.error(f"Redis connection failed: {e}")
        raise e
    finally:
        try:
            redis_client.close()
        except:
            pass


async def run_periodic_task(periodic_task: callable, seconds_to_sleep: int) -> None:
    while True:
        await asyncio.wait_for(periodic_task(), timeout=None)
        await asyncio.sleep(seconds_to_sleep)


def run_scheduler() -> None:
    loop = asyncio.new_event_loop()
    task = loop.create_task(run_periodic_task(update_config_cache_task, settings.CONFIGS_CACHE_UPDATE_EVERY_SECONDS))
    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass


async def health_checks() -> None:
    logger.info("Running pre-start checks...")
    
    # Check database
    logger.info("Checking database connection...")
    await db_health_check(engine)
    logger.info("Database check completed")

    # Check Redis
    logger.info("Checking Redis connection...")
    redis_health_check()
    logger.info("Redis check completed")


if __name__ == "__main__":
    asyncio.run(health_checks())
    run_scheduler()
