from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MarketingData(Base):
    __tablename__ = "marketing_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    search_volume = Column(Integer, nullable=False)

class SalesData(Base):
    __tablename__ = "sales_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    revenue = Column(Integer, nullable=False)
