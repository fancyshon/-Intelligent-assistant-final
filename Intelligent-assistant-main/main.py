from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import Config

from routers import login, predict, stock, coin
from routers import inter


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stock.router)
app.include_router(coin.router)
app.include_router(login.router)
app.include_router(inter.router)
app.include_router(predict.router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT) 