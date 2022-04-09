from fastapi import APIRouter
from bs4 import BeautifulSoup 
import urllib.request

from database import SESSION
from database import Coin, database_Favorite_coin

router = APIRouter()


@router.get("/coin")
async def get_coin(name: str):
    return get_coin_info(name)


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