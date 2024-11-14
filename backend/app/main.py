from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.main import api_router
from app.api.routes.assign_order import service


@asynccontextmanager
async def lifespan(app: FastAPI):   # noqa
    is_config_cache_updated = await service.data_provider.update_config_cache()
    if not is_config_cache_updated:
        raise Exception("Can not receive initial data from config on startup and update cache with it")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(api_router, prefix=settings.API_V1_STR)
