import httpx
import asyncio
from app.app_logger import logger

from app.api.routes.assign_order import service


async def update_config_cache_task() -> None:
    logger.info('Updating config cache')
    # бесконечный цикл повторных запросов к сервису конфига, пока он не ответит
    cache_not_updated = True
    while cache_not_updated:
        try:
            # хотим ровно один вызов к конфиг сервису
            await asyncio.wait_for(service.data_provider.update_config_cache(), timeout=None)
            cache_not_updated = False
        # детальное логирование ошибок сделано ближе к самому rpc вызову
        except: # noqa
            logger.error(f"Got exception during updating config cache, retrying")
    logger.info('Config cache updated')
