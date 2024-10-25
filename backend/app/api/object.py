import httpx

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.object import object_
from app.database.dependencies import get_db
from app.schemas.object import Object, ListObjects

objects_router = APIRouter()


@objects_router.post("/create_and_list", status_code=201, response_model=ListObjects)
async def call_create_and_list() -> Any:
    """
    Create a new object in the database and lists all objects.
    """
    async with httpx.AsyncClient() as client:
        await client.post(f'http://127.0.0.1:8001/objects/create_object')
        objects = await client.post(f'http://127.0.0.1:8001/objects/list_all')
    return objects.json()


@objects_router.get("/{object_id}", status_code=200, response_model=Object)
async def get_object_by_id(
        *,
        object_id: int,
        db: Session = Depends(get_db),
) -> Any:
    """
    Fetch a single object by id.
    """
    result = await object_.get_by_id(db=db, requested_id=object_id)
    if not result:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Object with id {object_id} not found"
        )

    return result


@objects_router.post("/list_all", status_code=201, response_model=ListObjects)
async def list_objects(*,
                       db: Session = Depends(get_db)) -> dict:
    """
    Fetch all objects.
    """
    objects = await object_.get_all(db=db)
    return {"results": list(objects)}


@objects_router.post("/create_object", status_code=201, response_model=Object)
async def create_object(
        *,
        db: Session = Depends(get_db),
) -> Object:
    """
    Create a new object in the database.
    """
    return await object_.create(db=db)


@objects_router.delete("/delete/{object_id}", status_code=201, response_model=Object)
async def delete_post(*, object_id: int,
                      db: Session = Depends(get_db)) -> dict:
    """
    Delete an object with specified id.
    """
    object_to_delete = await get_object_by_id(object_id=object_id, db=db)

    return await object_.delete(db=db, object_to_delete=object_to_delete)
