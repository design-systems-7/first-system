from contextlib import asynccontextmanager

from fastapi import FastAPI
import logging
import asyncio, time

from app.api.main import api_router
from app.api.routes.assign_order import service
from app.core.config import settings
from app.database.db import engine
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await service.data_provider.update_config_cache()
        logger.info("Application startup complete")
        yield
        
    finally:
        
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
            
            
            try:
                await service.data_provider.close()
                logger.info("Redis connections closed")
            except Exception as e:
                logger.error(f"Error closing Redis connections: {e}")
            
            # 5. Отмена фоновых задач - не работает при тестах. TODO: app.state.tasks = set()
            # tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            # for task in tasks:
            #     task.cancel()
            # await asyncio.gather(*tasks, return_exceptions=True)
            
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
