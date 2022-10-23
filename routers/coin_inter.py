import re
from fastapi import APIRouter
from database import SESSION
import numpy as np
import pandas as pd
import json
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

@router.get("/coin_inter")
async def basic_draw(Crypto: str):
    try:
        res = requests.get('https://min-api.cryptocompare.com/data/histohour?fsym=' + Crypto + '&tsym=USD&limit=72')
        btc_input_df = pd.DataFrame(json.loads(res.content)['Data'])
        stamp = btc_input_df['time'][0]
        for i in range(0, 1):
            res = requests.get('https://min-api.cryptocompare.com/data/histohour?fsym=' + Crypto + '&tsym=USD&limit=72' + '&toTs=' + str(stamp))
            temp = pd.DataFrame(json.loads(res.content)['Data'])
            stamp = temp['time'][0]
        btc_input_df = btc_input_df.append(temp)
        btc_input_df = btc_input_df.drop(['conversionType'], axis=1)
        btc_input_df = btc_input_df.drop(['conversionSymbol'], axis=1)
        btc_input_df = btc_input_df.drop(['volumefrom'], axis=1)
        btc_input_df.columns = ['Date','High','Low','Open','Volume','Close']
        btc_input_df = btc_input_df.set_index('Date')
        btc_input_df = btc_input_df.sort_index()
        btc_input_df.index = pd.to_datetime(btc_input_df.index, unit='s')
        address = "./routers/datasets/" + Crypto + ".csv"
        btc_input_df.to_csv(address)
        df = pd.read_csv(address)
        df.index = pd.DatetimeIndex(df['Date'])
        df =df.drop(['Date'],axis = 1)

        ## KD_draw
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
        address1 = "./routers/coin_image/" + Crypto + "kd.jpg"
        #%m-%d %H:%M:%S
        xmin = len(df_kd_draw)*0.15
        xmax = len(df_kd_draw)
        kwargs = dict(type='candle', mav=(5,10,20), volume = True,figsize=(12.5,12),datetime_format='%m-%d %H:%M', style=s,addplot=add_plot, xlim=(xmin,xmax) ,tight_layout=True )
        mpf.plot(df_kd_draw, **kwargs,savefig = address1)

        ## macd
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
        xmin = len(data_frame)*0.15
        xmax = len(data_frame)
        kwargs = dict(type='candle', mav=(5,10,20), volume = True,figsize=(12.5,12), style=s,addplot=add_plot,datetime_format='%m-%d %H:%M', xlim=(xmin,xmax) ,tight_layout=True )
        address = "./routers/coin_image/" + Crypto + "macd.jpg"
        mpf.plot(data_frame, **kwargs , savefig=address)

        ## golden
        df_kd_skill = df
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
        xmin = len(df_kd_skill)*0.15
        xmax = len(df_kd_skill)
        kwargs = dict(type='candle', volume = True,figsize=(12.5,12), style=s,addplot=add_plot,datetime_format='%m-%d %H:%M', xlim=(xmin,xmax) ,tight_layout=True )        
        address = "./routers/coin_image/" + Crypto + "golden.jpg"
        mpf.plot(df_kd_skill, **kwargs ,savefig=address)

        ## macd_op
        a=MACD_Buy_Sell(df)
        df['Buy_Signal_Price']=a[0]
        df['Sell_Signal_Price']=a[1]
        plt.figure(figsize=(12.5,4.5))
        plt.scatter(df.index,df['Buy_Signal_Price'],color='red', label='Buy',marker='^',alpha=1)
        plt.scatter(df.index,df['Sell_Signal_Price'],color='green', label='Sell',marker='v',alpha=1)
        plt.plot(df['Close'], label='Close Price', alpha=0.35)
        address = "./routers/coin_image/" + Crypto + "macdop.jpg"
        plt.xticks(rotation=45)
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend(loc='upper left')
        plt.savefig(address, bbox_inches="tight", pad_inches=0)

        ## boolean
        df_boolean_draw = df
        df_boolean_draw["upper"],df_boolean_draw["middle"],df_boolean_draw["lower"] = talib.BBANDS(df_boolean_draw["Close"], timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)

        add_plot =[mpf.make_addplot(df_boolean_draw[['upper','lower']],linestyle='dashdot'),
                mpf.make_addplot(df_boolean_draw['middle'],linestyle='dotted',color='y'),
                mpf.make_addplot(df_boolean_draw["K"],panel= 2,color="b"),
                mpf.make_addplot(df_boolean_draw["D"],panel= 2,color="r")
                ]
        mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        xmin = len(df_boolean_draw)*0.15
        xmax = len(df_boolean_draw)
        kwargs = dict(type='candle',  volume = True,figsize=(12.5,12), style=s,addplot=add_plot,datetime_format='%m-%d %H:%M', xlim=(xmin,xmax) ,tight_layout=True )
        address = "./routers/coin_image/" + Crypto + "bool.jpg"
        mpf.plot(df_boolean_draw, **kwargs ,savefig=address)

        ## RSI
        df['RSI6'] = talib.RSI(df['Close'],timeperiod = 6)
        df['RSI12'] = talib.RSI(df['Close'],timeperiod = 12)
        add_plot =[mpf.make_addplot(df["RSI6"],panel= 2,color="b"),
        mpf.make_addplot(df["RSI12"],panel= 2,color="r")]
        mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        xmin = len(df)*0.15
        xmax = len(df)
        kwargs = dict(type='candle', mav=(5,10,20), volume = True,figsize=(12.5,12), style=s,addplot=add_plot,datetime_format='%m-%d %H:%M', xlim=(xmin,xmax) ,tight_layout=True )
        address = "./routers/coin_image/" + Crypto + "rsi.jpg"
        mpf.plot(df, **kwargs, savefig=address)
    except:
        print("輸入錯誤格式，請重新輸入")
    
    CLIENT_ID = "d8da624901bac06"
    PATH = "./routers/coin_image/" + Crypto + "kd.jpg"
    uploadedImg = pyimgur.Imgur(CLIENT_ID).upload_image(PATH, title = 'fucjnfdio')
    return uploadedImg.link

@router.get("/coin_macd")
async def coin_macd(Crypto: str):
    CLIENT_ID = "d8da624901bac06"
    PATH = "./routers/coin_image/" + Crypto + "macd.jpg"
    uploadedImg = pyimgur.Imgur(CLIENT_ID).upload_image(PATH, title = 'fucjnfdio')
    return uploadedImg.link

@router.get("/coin_golden")
async def coin_golden(Crypto: str):
    CLIENT_ID = "d8da624901bac06"
    PATH = "./routers/coin_image/" + Crypto + "golden.jpg"
    uploadedImg = pyimgur.Imgur(CLIENT_ID).upload_image(PATH, title = 'fucjnfdio')
    return uploadedImg.link

@router.get("/coin_macdop")
async def coin_macdop(Crypto: str):
    CLIENT_ID = "d8da624901bac06"
    PATH = "./routers/coin_image/" + Crypto + "macdop.jpg"
    uploadedImg = pyimgur.Imgur(CLIENT_ID).upload_image(PATH, title = 'fucjnfdio')
    return uploadedImg.link

@router.get("/coin_bool")
async def coin_bool(Crypto: str):
    CLIENT_ID = "d8da624901bac06"
    PATH = "./routers/coin_image/" + Crypto + "bool.jpg"
    uploadedImg = pyimgur.Imgur(CLIENT_ID).upload_image(PATH, title = 'fucjnfdio')
    return uploadedImg.link

@router.get("/coin_rsi")
async def coin_rsi(Crypto: str):
    CLIENT_ID = "d8da624901bac06"
    PATH = "./routers/coin_image/" + Crypto + "rsi.jpg"
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
