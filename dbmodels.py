from sqlalchemy import Column, Integer, String, Numeric
from database import Base


class StockData(Base):
    __tablename__ = "StockData"

    id = Column(Integer, primary_key=True, index=True)
    stockname = Column(String, unique= True, index=True)
    price = Column(Numeric(10,2))
    forward_pe = Column(Numeric(10,2))
    forward_eps = Column(Numeric(10,2))
    dividend_yield = Column(Numeric(10,2))
    ma50 = Column(Numeric(10,2))
    ma200 = Column(Numeric(10,2))
    