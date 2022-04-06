from fastapi import FastAPI
from config import Config

from routers import home, server, inter, predict

from fakedata import add_fakedata



app = FastAPI()
app.include_router(home.router)
app.include_router(server.router)
app.include_router(inter.router)
app.include_router(predict.router)


if Config.FAKE_DATA == "true":
    add_fakedata()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT) 