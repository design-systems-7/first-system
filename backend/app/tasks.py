from time import sleep

from app.app_logger import logger
from app.api.routes.assign_order import service
from app.core.config import settings


async def update_config_cache_task() -> None:
    logger.info('Updating config cache')
    cache_updated = False
    while not cache_updated:
        cache_updated = await service.data_provider.update_config_cache()
        if not cache_updated:
            logger.error(f"Got error during updating config cache, retrying.")
        sleep(settings.TASK_WAIT_BEFORE_RETRY_IN_SECONDS)
    logger.info('Config cache updated')


async def close_redis_connection():
    return await service.data_provider.close()
