from fastapi import APIRouter

from app.api import object

api_router = APIRouter()
api_router.include_router(object.objects_router, prefix="/objects", tags=["objects"])
