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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

async def init_config_cache() -> None:
    try:
        logger.info('Initializing config cache')
        success = False
        for attempt in range(max_tries):
            success = await update_config_cache_task()
            if success:
                logger.info('Config cache initialized successfully')
                break
            logger.warning(f'Config cache initialization attempt {attempt + 1} failed, retrying...')
            await asyncio.sleep(wait_seconds)
        
        if not success:
            raise Exception("Failed to initialize config cache after all attempts")
    finally:
        await close_redis_connection()
        

async def main() -> None:
    logger.info("Running pre-start checks...")
    
    # Check database
    logger.info("Checking database connection...")
    await db_health_check(engine)
    logger.info("Database check completed")

    # Check Redis
    logger.info("Checking Redis connection...")
    redis_health_check()
    logger.info("Redis check completed")

    # Initialize config once
    logger.info("Initializing config...")
    await init_config_cache()
    logger.info("Config initialization completed")

if __name__ == "__main__":
    asyncio.run(main())