from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.object import Object
from app.schemas.object import ObjectCreate, ObjectUpdate


class CRUDObject(CRUDBase[Object, ObjectCreate, ObjectUpdate]):
    # def create(self, db: Session, *, obj_in: ObjectCreate) -> Object:
    async def create(self, db: AsyncSession, *, obj_in='') -> Object:
        # in template argument is marked as unexpected because Object schemas do not contain attributes
        # db_object = self.model(**jsonable_encoder(obj_in))
        db_object = self.model()

        db.add(db_object)

        await db.commit()
        # await db.refresh(db_object)

        return db_object

    async def update(self, db: AsyncSession, *,
                     db_object: Object,
                     object_in: ObjectUpdate) -> Object:

        return await super().update(db, db_object=db_object, object_in=object_in)

    async def delete(self, db: AsyncSession, *, object_to_delete: Object) -> Object:
        return await super().delete(db, object_to_delete=object_to_delete)


object_ = CRUDObject(Object)
