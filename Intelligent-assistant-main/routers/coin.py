from fastapi import APIRouter
from bs4 import BeautifulSoup 
import urllib.request

from database import SESSION
from database import Coin, database_Favorite_coin

router = APIRouter()


@router.get("/coin")
async def get_coin(name: str):
    return get_coin_info(name)

@router.get("/favorite_coin")
async def get_favorite_coin(user: str):
    user_favorite_coin = SESSION.query(database_Favorite_coin).filter(database_Favorite_coin.user == user).all()
    data = []
    for favorite_list in user_favorite_coin:
        data.append(get_coin_info(favorite_list.name))
    return data

@router.post("/favorite_coin")
async def post_favorite_coin(user: str, name: str):
    if SESSION.query(database_Favorite_coin).filter(database_Favorite_coin.user == user, database_Favorite_coin.name == name).first() is None:
        new_favorite_coin = database_Favorite_coin(
            **{
                "name": name,
                "user": user
            }
        )
        SESSION.add(new_favorite_coin)
        SESSION.commit()
        SESSION.refresh(new_favorite_coin)
    return "successfully"

@router.delete("/favorite_coin")
async def delete_favorite_coin(user: str, name: str):
    SESSION.query(database_Favorite_coin).filter(database_Favorite_coin.user == user, database_Favorite_coin.name == name).delete()
    SESSION.commit()
    return "successfully"


def get_coin_info(name: str):
    data =  Coin(
        **{
            "name": name,
            "high_price": 0,
            "low_price": 0,
            "now_price": 0,
            "price_increase": 0,
            "price_increase_rate": 0
        }
    )
    text_request = urllib.request.urlopen("https://crypto.cnyes.com/"+name+"/24h")
    soup = BeautifulSoup(text_request,"html.parser")
    data.now_price = soup.find('span', {'class': 'jsx-143270965 big-num'}).text + soup.find('span', {'class': 'jsx-143270965 small-num'}).text
    price_high_low = soup.find_all('div', {'class': 'jsx-3999696274 item-value'})
    data.high_price = price_high_low[0].text
    data.low_price = price_high_low[1].text
    price_increase = soup.find('span', {'class': 'jsx-143270965 ch is-positive'})
    if price_increase is None:
        price_increase = soup.find('span', {'class': 'jsx-143270965 ch is-negative'})
        data.price_increase = "-" + price_increase.text
    else:
        data.price_increase = "+" + price_increase.text
    # price increase rate
    price_increase_rate = soup.find('span', {'class': 'jsx-143270965 chp is-positive'})
    if price_increase_rate is None:
        price_increase_rate = soup.find('span', {'class': 'jsx-143270965 chp is-negative'})
        data.price_increase_rate = "-" + price_increase_rate.text
    else:
        data.price_increase_rate = "+" + price_increase_rate.text
    return data