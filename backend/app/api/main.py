from fastapi import APIRouter

from app.api.routes import assign_order, cancel_order, utils

api_router = APIRouter()
api_router.include_router(assign_order.router, prefix="/assign_order", tags=["order"])
api_router.include_router(cancel_order.router, prefix="/cancel_order", tags=["order"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
