from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union, Sequence

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateType = TypeVar("CreateType", bound=BaseModel)
UpdateType = TypeVar("UpdateType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateType, UpdateType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    # pass because usually every model has its own create function
    async def create(self, db: AsyncSession, *, obj_in: CreateType) -> ModelType:
        pass

    async def get_by_id(self, db: AsyncSession, requested_id: Any) -> Optional[ModelType]:
        result = (await db.execute(select(self.model).where(self.model.id == requested_id))).first()
        if result:
            # result is a tuple with only one item
            return result[0]
        else:
            return None

    async def get_all(self, db: AsyncSession) -> Sequence[ModelType]:
        return (await db.execute(select(self.model).order_by(self.model.id))).scalars().all()

    async def update(self, db: AsyncSession, *,
                     db_object: ModelType,
                     object_in: Union[UpdateType, Dict[str, Any]]) -> ModelType:

        if isinstance(object_in, dict):
            update_data = object_in
        else:
            update_data = object_in.dict(exclude_unset=True)

        db_object_data = jsonable_encoder(db_object)
        for field in db_object_data:
            if field in update_data:
                # = assignment (db_object.field = update_data[field]) will not work
                setattr(db_object, field, update_data[field])

        db.add(db_object)
        await db.commit()
        await db.refresh(db_object)

        return db_object

    async def delete(self, db: AsyncSession, *, object_to_delete: ModelType) -> ModelType:
        await db.delete(object_to_delete)
        await db.commit()

        return object_to_delete

