from pydantic import BaseModel

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy import Column, Integer, String, Float


# initialize database
SQLALCHEMY_DATABASE_URL = "sqlite:///database.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SESSION: Session = sessionmaker(bind=engine)() 
Base = declarative_base()


# set database table
class database_Stock(Base):
    __tablename__ = "stock"

    number = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    start_price = Column(Float, nullable=False)
    now_price = Column(Float, nullable=False)
    price_increase = Column(Float, nullable=False)

class database_Favorite(Base):
    __tablename__ = "favorite"

    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False)
    user = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)


# set model
class Stock(BaseModel):
    number: int
    name: str
    high_price: float
    low_price: float
    start_price: float
    now_price: float
    price_increase: float

class Favorite(BaseModel):
    id: int
    number: int
    user: str