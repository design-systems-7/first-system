from sqlalchemy import Column, Integer
from sqlalchemy.orm import as_declarative, declared_attr


# using declarative style
@as_declarative()
class Base:
    __name__: str

    # generate __tablename__ automatically
    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()

    # unique and index constraints are redundant in case of single column of "Integer" type
    # https://www.sqlite.org/lang_createtable.html#rowid
    id = Column(Integer, primary_key=True)
