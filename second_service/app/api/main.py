from fastapi import APIRouter

from app.api.routes import issue_order, utils

api_router = APIRouter()
api_router.include_router(issue_order.router, prefix="/issue_order", tags=["order"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
