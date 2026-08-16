from sqlalchemy import Column, Integer, String
from .database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key = True, index = True)
    customer_name = Column(String, nullable = False)
    customer_email = Column(String, nullable=False)
    product = Column(String, nullable = False)
    status = Column(String, default = "pending")
