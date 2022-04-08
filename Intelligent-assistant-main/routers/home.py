import re
from fastapi import APIRouter
from bs4 import BeautifulSoup 
import urllib.request

from database import SESSION
from database import Stock, database_Favorite

router = APIRouter()


@router.get("/stock")
async def get_stock(number: str):
    return get_stock_info(number)

@router.get("/favorite")
async def get_favorite(user: str):
    user_favorite = SESSION.query(database_Favorite).filter(database_Favorite.user == user).all()
    broad_market_index = Stock(
        **{
            "number": 0,
            "name": "大盤指數",
            "high_price": 17500,
            "low_price": 17304,
            "start_price": 17444,
            "now_price": 17374,
            "price_increase": (17374-17444),
            "yesterday_price": 0
        }
    )
    data = [broad_market_index]
    for favorite_list in user_favorite:
        data.append(get_stock_info(favorite_list.number))
    return data

@router.post("/favorite")
async def post_favorite(user: str, number: str):
    if SESSION.query(database_Favorite).filter(database_Favorite.user == user, database_Favorite.number == number).first() is None:
        new_favorite = database_Favorite(
            **{
                "number": number,
                "user": user
            }
        )
        SESSION.add(new_favorite)
        SESSION.commit()
        SESSION.refresh(new_favorite)
    return "successfully"


def get_stock_info(stock_number: str):
    data =  Stock(
        **{
            "number": stock_number,
            "name": '',
            "high_price": 0,
            "low_price": 0,
            "start_price": 0,
            "now_price": 0,
            "price_increase": 0,
            "yesterday_price": 0
        }
    )
    if stock_number != "0000":
        text_request = urllib.request.urlopen("https://tw.stock.yahoo.com/quote/"+stock_number)
        soup = BeautifulSoup(text_request,"html.parser")
        data.name = soup.find('h1', {'class': 'C($c-link-text) Fw(b) Fz(24px) Mend(8px)'}).text
        price_data = soup.find_all('span')
        if price_data[68].text == "成交":
            data.now_price = price_data[69].text
            data.start_price = price_data[71].text
            data.high_price = price_data[73].text
            data.low_price = price_data[75].text
            data.yesterday_price = price_data[81].text
            data.price_increase = round(float(data.now_price) - float(data.yesterday_price), 2)
        elif price_data[70].text == "成交":
            data.now_price = price_data[71].text
            data.start_price = price_data[73].text
            data.high_price = price_data[75].text
            data.low_price = price_data[77].text
            data.yesterday_price = price_data[83].text
            data.price_increase = round(float(data.now_price) - float(data.yesterday_price), 2)
    return data