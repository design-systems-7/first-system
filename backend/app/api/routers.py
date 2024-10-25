from fastapi import APIRouter

from app.api import object
from app.api import assign_order_service

api_router = APIRouter()
api_router.include_router(object.objects_router, prefix="/objects", tags=["objects"])
api_router.include_router(assign_order_service.assign_order_service_router)
