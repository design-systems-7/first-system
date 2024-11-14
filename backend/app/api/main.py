from fastapi import APIRouter

from app.api.routes import assign_order, utils

api_router = APIRouter()
api_router.include_router(assign_order.router, prefix="", tags=["order"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
