from contextlib import asynccontextmanager
import asyncio
import time

from fastapi import FastAPI

from app.core.config import settings
from app.api.main import api_router
from app.api.routes.assign_order import service
from app.app_logger import logger
from app.database.db import engine


@asynccontextmanager
async def lifespan(app: FastAPI):   # noqa
    # Here can be enabled eternal retries if this is more desired behaviour
    is_config_cache_updated = await service.data_provider.update_config_cache()
    if not is_config_cache_updated:
        raise Exception("Can not receive initial data from config on startup and update cache with it")

    yield

    logger.info("Starting graceful shutdown...")
    try:
        app.state.accepting_requests = False
        if hasattr(app.state, 'active_requests'):
            timeout = 30  # секунд
            start_time = time.time()
            while app.state.active_requests > 0:
                if time.time() - start_time > timeout:
                    logger.warning(f"Shutdown timeout: {app.state.active_requests} requests still active")
                    break
                await asyncio.sleep(0.1)

        try:
            await engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
            pass

        try:
            await service.data_provider.close()
            logger.info("Redis connections closed")
        except Exception as e:
            logger.error(f"Error closing Redis connections: {e}")
            pass

        logger.info("Graceful shutdown complete")

    except Exception as e:
        logger.error(f"Error during graceful shutdown: {e}")
        raise


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(api_router, prefix=settings.API_V1_STR)
