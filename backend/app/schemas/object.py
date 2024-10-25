from typing import Sequence

from pydantic import BaseModel

# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-pydantic-models
# not a @dataclass because dict() method is required in CRUD


class ObjectBase(BaseModel):
    pass


class ObjectCreate(ObjectBase):
    pass


class ObjectUpdate(ObjectBase):
    pass


class Object(ObjectBase):
    id: int

    # https://fastapi.tiangolo.com/tutorial/sql-databases/#use-pydantics-orm_mode
    class Config:
        orm_mode = True


class ListObjects(BaseModel):
    results: Sequence[Object]
