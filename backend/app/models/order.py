from app.models.base_class import Base
from sqlalchemy import Column, Integer


# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-database-models
# no need for __tablename__ because of declarative style (app.database.base_class)
class Order(Base):
    order_id = Column(Integer, primary_key=True)
