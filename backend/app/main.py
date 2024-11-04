import asyncio

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.logging import logger
from app.api.main import api_router
from app.periodic_task_wrapper import repeat_every
from app.api.routes.assign_order import service


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


# TODO переделать
# Это то, как хочется видеть таску.
# Но, к сожалению, так она исполняется по разу каждым воркером, что точно не то, чего мы хотим
# Предлагается переделать это. Для избежания оверхеда планирую создать еще один сервис
# В нем будет чистый Python + aiocache, и через что-то вроде scheduler будет все то же самое обновляться
# В текущем виде еще баг с TransportClosed появляется

# @app.on_event("startup")
# @repeat_every(seconds=settings.CONFIG_CACHE_UPDATE_EVERY_SECONDS)
# def update_config_cache_task() -> None:
#     # бесконечный цикл повторных запросов к сервису конфига, пока он не ответит
#     cache_not_updated = True
#     while cache_not_updated:
#         try:
#             # хотим ровно один вызов к конфиг сервису
#             asyncio.run(asyncio.wait_for(service.data_provider.update_config_cache(), timeout=None))
#             cache_not_updated = False
#         # детальное логирование ошибок сделано ближе к самому rpc вызову
#         except: # noqa
#             logger.error(f"Got exception during updating config cache, retrying")
