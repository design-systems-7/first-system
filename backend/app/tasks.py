from app.app_logger import logger

from app.api.routes.assign_order import service


async def update_config_cache_task() -> None:
    logger.info('Updating config cache')
    cache_updated = False
    while not cache_updated:
        cache_updated = await service.data_provider.update_config_cache()
        if not cache_updated:
            logger.error(f"Got error during updating config cache, retrying.")
    logger.info('Config cache updated')
