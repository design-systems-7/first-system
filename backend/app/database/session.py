import asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

from app.database.base import *

# https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
# turn on 'echo=True' only for testing purposes
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl
# engine.sync_engine because async events is not yet implemented
# https://github.com/sqlalchemy/sqlalchemy/discussions/6594#discussioncomment-836437
@event.listens_for(engine.sync_engine, "connect")
def do_connect(dbapi_connection, connection_record):
    # disable pysqlite's emitting of the BEGIN statement entirely.
    # also stops it from emitting COMMIT before any DDL.
    dbapi_connection.isolation_level = None

    cursor = dbapi_connection.cursor()
    # https://www.sqlite.org/wal.html
    # Reading and writing can proceed concurrently
    cursor.execute("PRAGMA journal_mode=WAL")
    # https://www.sqlite.org/pragma.html#pragma_synchronous
    cursor.execute('PRAGMA synchronous=NORMAL')
    # https://www.sqlite.org/pragma.html#pragma_busy_timeout
    # set busy timeout to 1 second
    cursor.execute('PRAGMA busy_timeout = 1000')
    cursor.close()

    
@event.listens_for(engine.sync_engine, "begin")
def do_begin(conn):
    # emit our own BEGIN
    conn.exec_driver_sql("BEGIN")

    
async def init_models() -> None:
    # create db tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(init_models())
