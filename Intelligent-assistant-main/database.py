from unicodedata import name
from pydantic import BaseModel

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy import Column, Integer, String


# initialize database
SQLALCHEMY_DATABASE_URL = "sqlite:///database.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SESSION: Session = sessionmaker(bind=engine)() 
Base = declarative_base()


# set database table
class database_Favorite(Base):
    __tablename__ = "favorite"

    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False)
    user = Column(String, nullable=False)

class database_Favorite_coin(Base):
    __tablename__ = "favorite_coin"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)


# set model
class Stock(BaseModel):
    number: str
    name: str
    high_price: str
    low_price: str
    start_price: str
    now_price: str
    price_increase: str
    yesterday_price: str

class Coin(BaseModel):
    name: str
    high_price: str
    low_price: str
    now_price: str
    price_increase: str
    price_increase_rate: str