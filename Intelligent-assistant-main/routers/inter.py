import re
from fastapi import APIRouter
from database import SESSION
from database import Stock, database_Stock, Favorite, database_Favorite
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import datetime as datetime
import talib
import requests
import pyimgur
from io import StringIO
from bs4 import BeautifulSoup
from backtesting import Backtest, Strategy 
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG

router = APIRouter()
time_end = datetime.date.today()
time_start = '2021-11-11'

@router.get("/stock_inter")
async def basic(id: int):
    # 爬蟲
    try:
        days = 24 * 60 * 60    #一天有86400秒 
        initial = datetime.datetime.strptime( '1970-01-01' , '%Y-%m-%d' )
        start = datetime.datetime.strptime( str(time_start) , '%Y-%m-%d' )
        end = datetime.datetime.strptime( str(time_end), '%Y-%m-%d' )
        period1 = start - initial
        period2 = end - initial
        s1 = period1.days * days
        s2 = period2.days * days
        url ="https://query1.finance.yahoo.com/v7/finance/download/"+"2330"+".TW?period1="+str(s1)+"&period2="+str(s2)+"&interval=1d&events=history&includeAdjustedClose=true" 
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"}
        response = requests.get(url,headers = headers)
        df = pd.read_csv(StringIO(response.text),index_col = "Date",parse_dates = ["Date"])
        df.index[::10]
        address = "./routers/datasets/" + "2330" + ".csv" #自己改路徑

        df_kd_draw = df
        df_kd_draw['K'], df_kd_draw['D'] = talib.STOCH(df_kd_draw['High'], 
                                         df_kd_draw['Low'], 
                                         df_kd_draw['Close'], 
                                         fastk_period=9,
                                         slowk_period=3,
                                         slowk_matype=1,
                                         slowd_period=3,
                                         slowd_matype=1)
        add_plot =[mpf.make_addplot(df_kd_draw["K"],panel= 2,color="b"),
        mpf.make_addplot(df_kd_draw["D"],panel= 2,color="r")]
        mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        #address = r"C:\Users\Server\Desktop\dataset\\" + stock_id+"kd_ptr" + ".csv" #自己改路徑
        #df_kd_draw.to_csv(address)
    
        kwargs = dict(type='candle', mav=(5,10,20,60), volume = True,title = str(id)+" KD picture", style=s,addplot=add_plot)
        address = "./routers/images/" + str(id) + "kd.jpg"
        mpf.plot(df_kd_draw, **kwargs, savefig=address)

        # macd_draw
        data_frame = df
        ShortEMA=data_frame.Close.ewm(span=12,adjust=False).mean()
        LongEMA=data_frame.Close.ewm(span=26,adjust=False).mean()
        MACD=ShortEMA-LongEMA
        signal=MACD.ewm(span=9,adjust=False).mean()
        data_frame['MACD'] = MACD
        data_frame['Signal'] = signal
        add_plot =[mpf.make_addplot(data_frame["MACD"],panel= 2,color="b"),
        mpf.make_addplot(data_frame["Signal"],panel= 2,color="r")]
        mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        kwargs = dict(type='candle', mav=(5,10,20,60), volume = True,figsize=(20, 10),title = str(id)+" MACD", style=s,addplot=add_plot)
        address = "./routers/images/" + str(id) + "macd.jpg"
        mpf.plot(data_frame, **kwargs, savefig=address)

        ## kd_golden
        df_kd_skill = df
        df_kd_skill = df_kd_skill.loc[time_start:]
        np.any(pd.isnull(df_kd_skill))
        df_kd_skill['K'], df_kd_skill['D'] = talib.STOCH(df_kd_skill['High'], 
                                                df_kd_skill['Low'], 
                                                df_kd_skill['Close'], 
                                                fastk_period=9,
                                                slowk_period=3,
                                                slowk_matype=1,
                                                slowd_period=3,
                                                slowd_matype=1)


        df_kd_skill["B_K"] = df_kd_skill["K"].shift(1)
        df_kd_skill["B_D"] = df_kd_skill["D"].shift(1)
        df_kd_skill.tail()

        buy = []
        for i in range(len(df_kd_skill)):
            if df_kd_skill["B_K"][i] <  df_kd_skill["B_D"][i] and df_kd_skill["K"][i] > df_kd_skill["D"][i]:
                buy.append(1)
            else:
                buy.append(0)
        df_kd_skill["buy"] = buy

        sell = []
        for i in range(len(df_kd_skill)):
            if df_kd_skill["B_K"][i] > df_kd_skill["B_D"][i] and df_kd_skill["K"][i]< df_kd_skill["D"][i]:
                sell.append(-1)
            else:
                sell.append(0)
        df_kd_skill["sell"] = sell

        buy_mark = []
        for i in range(len(df_kd_skill)):
            if df_kd_skill["buy"][i] == 1:
                buy_mark.append(df_kd_skill["High"][i] + 10)
            else:
                buy_mark.append(np.nan)
        df_kd_skill["buy_mark"] = buy_mark

        sell_mark = []
        for i in range(len(df_kd_skill)):
            if df_kd_skill["sell"][i] == -1:
                sell_mark.append(df_kd_skill["Low"][i] - 10)
            else:
                sell_mark.append(np.nan)
        df_kd_skill["sell_mark"] = sell_mark
        df_kd_skill.index  = pd.DatetimeIndex(df_kd_skill.index)
        mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        add_plot =[mpf.make_addplot(df_kd_skill["buy_mark"],scatter=True, markersize=100, marker='v', color='r'),
                mpf.make_addplot(df_kd_skill["sell_mark"],scatter=True, markersize=100, marker='^', color='g'),
                mpf.make_addplot(df_kd_skill["K"],panel= 2,color="b"),
                mpf.make_addplot(df_kd_skill["D"],panel= 2,color="r")]
        kwargs = dict(type='candle', volume = True,title = str(id)+"KDoperation", style=s,addplot=add_plot)
        address = "./routers/images/" + str(id) + "golden.jpg" 
        mpf.plot(df_kd_skill, **kwargs, savefig=address)

        ## macd_op
        a=MACD_Buy_Sell(df)
        df['Buy_Signal_Price']=a[0]
        df['Sell_Signal_Price']=a[1]
        plt.figure(figsize=(12.2,4.5))
        plt.scatter(df.index,df['Buy_Signal_Price'],color='red', label='Buy',marker='^',alpha=1)
        plt.scatter(df.index,df['Sell_Signal_Price'],color='green', label='Sell',marker='v',alpha=1)
        plt.plot(df['Close'], label='Close Price', alpha=0.35)
        plt.title('MACD operation')
        plt.xticks(rotation=45)
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend(loc='upper left')
        # plt.show()
        address = "./routers/images/" + str(id) + "macdop.jpg" 
        plt.savefig(address)

        ##　boolean
        df_boolean_draw = df
        df_boolean_draw["upper"],df_boolean_draw["middle"],df_boolean_draw["lower"] = talib.BBANDS(df_boolean_draw["Close"], timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)

        add_plot =[mpf.make_addplot(df_boolean_draw[['upper','lower']],linestyle='dashdot'),
                mpf.make_addplot(df_boolean_draw['middle'],linestyle='dotted',color='y'),
                ]
        mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        kwargs = dict(type='candle', volume = True,figsize=(20, 10),title = str(id)+"boolean", style=s,addplot=add_plot)
        address = "./routers/images/" + str(id) + "bool.jpg" 
        mpf.plot(df_boolean_draw, **kwargs, savefig=address)
    except:
        print("輸入錯誤格式，請重新輸入")
    
    CLIENT_ID = "b57c8df3844ca8d"
    PATH = "./routers/images/"+str(id)+"kd.jpg"
    uploadedImg = pyimgur.Imgur(CLIENT_ID).upload_image(PATH, title = 'fucjnfdio')
    return uploadedImg.link

@router.get("/golden")
async def kd(id: int):
    CLIENT_ID = "b57c8df3844ca8d"
    PATH = "./routers/images/"+str(id)+"golden.jpg"
    uploadedImg = pyimgur.Imgur(CLIENT_ID).upload_image(PATH, title = 'fucjnfdio')
    return uploadedImg.link

@router.get("/bool")
async def bool(id: int):
    CLIENT_ID = "b57c8df3844ca8d"
    PATH = "./routers/images/"+str(id)+"bool.jpg"
    uploadedImg = pyimgur.Imgur(CLIENT_ID).upload_image(PATH, title = 'fucjnfdio')
    return uploadedImg.link

@router.get("/macd")
async def macd(id: int):
    CLIENT_ID = "b57c8df3844ca8d"
    PATH = "./routers/images/"+str(id)+"macd.jpg"
    uploadedImg = pyimgur.Imgur(CLIENT_ID).upload_image(PATH, title = 'fucjnfdio')
    return uploadedImg.link

@router.get("/macdop")
async def macdop(id: int):
    CLIENT_ID = "b57c8df3844ca8d"
    PATH = "./routers/images/"+str(id)+"macdop.jpg"
    uploadedImg = pyimgur.Imgur(CLIENT_ID).upload_image(PATH, title = 'fucjnfdio')
    return uploadedImg.link

def MACD_Buy_Sell(signal):
    Buy=[]
    Sell=[]
    flag=-1
    for i in range(0,len(signal)):
        if signal['MACD'][i] > signal['Signal'][i]:
            Sell.append(np.nan)
            if flag !=1:
                Buy.append(signal['Close'][i])
                flag=1
            else:
                Buy.append(np.nan)
        elif signal['MACD'][i] < signal['Signal'][i]:
            Buy.append(np.nan)
            if flag !=0:
                Sell.append(signal['Close'][i])
                flag=0
            else:
                Sell.append(np.nan)
        else:
            Buy.append(np.nan)
            Sell.append(np.nan)
    return(Buy,Sell)