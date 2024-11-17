from app.api.routes.assign_order import service
from app.app_logger import logger


async def update_config_cache_task() -> bool:
    try:
        logger.info('Updating config cache')
        return await service.data_provider.update_config_cache()
    except Exception as e:
        logger.error(f"Error updating config cache: {e}")
        return False

async def close_redis_connection():
    return await service.data_provider.close()
    