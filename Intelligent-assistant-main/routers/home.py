from fastapi import APIRouter

from database import SESSION
from database import Stock, database_Stock, Favorite, database_Favorite

router = APIRouter()

@router.get("/stock")
async def get_stock(numbers: int):
    stock_info = SESSION.query(database_Stock).filter(database_Stock.number == numbers).first()
    return stock_info

@router.get("/user")
async def get_favorite(user: str):
    user_favorite = SESSION.query(database_Favorite).filter(database_Favorite.user == user).all()
    broad_market_index = database_Stock(
        **{
            "number": 0,
            "name": "大盤指數",
            "high_price": 17500,
            "low_price": 17304,
            "start_price": 17444,
            "now_price": 17374,
            "price_increase": (17374-17444)
        }
    )
    data = [broad_market_index]
    for favorite_list in user_favorite:
        stock_info = SESSION.query(database_Stock).filter(database_Stock.number == favorite_list.number).first()
        data.append(stock_info)
    return data


def add_stock(stock_info: Stock):
    new_stack_info = database_Stock(
        **{
            "number": stock_info.number,
            "name": stock_info.name,
            "high_price": stock_info.high_price,
            "low_price": stock_info.low_price,
            "start_price": stock_info.start_price,
            "now_price": stock_info.now_price,
            "price_increase": stock_info.price_increase
        }
    )
    SESSION.add(new_stack_info)
    SESSION.commit()
    SESSION.refresh(new_stack_info)