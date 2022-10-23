from fastapi import APIRouter

import routers.Predict_Crypto
import routers.Predict_Stock

router = APIRouter()

@router.get("/predict_stock")
async def predict_stock(number: str):
    predict_price, predict_per = routers.Predict_Stock.Predict(number)
    return predict_price, predict_per

@router.get("/predict_coin")
async def predict_coin(name: str):
    predict_price, predict_per = routers.Predict_Crypto.Predict(name)
    return predict_price, predict_per