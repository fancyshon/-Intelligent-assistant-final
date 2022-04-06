import json

from database import SESSION
from database import database_Stock, database_Favorite


def add_fakedata():
    #stock fakedata
    fakedata_stock = json.load(open("fakedata_stock.json"))
    for data in fakedata_stock:
        new_stock = database_Stock(
            **{
                "number": int(data["number"]),
                "name": data["name"],
                "high_price": float(data["high_price"]),
                "low_price": float(data["low_price"]),
                "start_price": float(data["start_price"]),
                "now_price": float(data["now_price"]),
                "price_increase": round(float(data["now_price"])-float(data["start_price"]),2)
            }
        )
        SESSION.merge(new_stock)
        SESSION.commit()
    
    #favorite fakedata
    fakedata_favorite = json.load(open("fakedata_favorite.json"))
    for data in fakedata_favorite:
        new_favorite = database_Favorite(
            **{
                "id": int(data["id"]),
                "number": int(data["number"]),
                "user": data["user"]
            }
        )
        SESSION.merge(new_favorite)
        SESSION.commit()