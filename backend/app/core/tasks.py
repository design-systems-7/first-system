from app.main import app
from app.periodic_task_wrapper import repeat_every
from app.core.config import settings
from app.api.routes.assign_order import service


@app.on_event("startup")
@repeat_every(seconds=settings.CONFIG_CACHE_UPDATE_EVERY_SECONDS)
def update_config_cache_task() -> None:
    service.data_provider.update_config_cache()
