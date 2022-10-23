import os
import pandas as pd
import numpy as np
import math
import requests
import json
import datetime as dt

from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score, r2_score
from sklearn.metrics import mean_poisson_deviance, mean_gamma_deviance, accuracy_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.layers import LSTM
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping


def dataset_generator_lstm(dataset, look_back=5):
    # A “lookback period” defines the window-size of how many
    # previous timesteps are used in order to predict
    # the subsequent timestep.
    dataX, dataY = [], []

    for i in range(len(dataset) - look_back):
        window_size_x = dataset[i:(i + look_back), :]
        dataX.append(window_size_x)
        dataY.append(dataset[i + look_back, 4])  # this is the label or actual y-value
    return np.array(dataX), np.array(dataY)


def Crypto_model(Crypto='BTC'):

    # Get Data
    res = requests.get('https://min-api.cryptocompare.com/data/histohour?fsym=' + Crypto + '&tsym=USD&limit=2000')
    btc_input_df = pd.DataFrame(json.loads(res.content)['Data'])
    stamp = btc_input_df['time'][0]
    for i in range(0, 4):
        res = requests.get('https://min-api.cryptocompare.com/data/histohour?fsym=' + Crypto + '&tsym=USD&limit=2000' + '&toTs=' + str(stamp))
        temp = pd.DataFrame(json.loads(res.content)['Data'])
        stamp = temp['time'][0]
    btc_input_df = btc_input_df.append(temp)
    btc_input_df = btc_input_df.set_index('time')
    btc_input_df.index = pd.to_datetime(btc_input_df.index, unit='s')

    btc_input_df = btc_input_df.sort_index()
    btc_input_df = btc_input_df.drop(['conversionType'], axis=1)
    btc_input_df = btc_input_df.drop(['conversionSymbol'], axis=1)
    btc_input_df = btc_input_df.drop(['volumeto'], axis=1)

    # Train Test Split
    btc_closing_price_groupby_date = btc_input_df
    prediction_hours = int(len(btc_closing_price_groupby_date) * 0.2)
    df_train = btc_closing_price_groupby_date.iloc[:len(btc_closing_price_groupby_date) - prediction_hours]
    df_test = btc_closing_price_groupby_date.iloc[len(btc_closing_price_groupby_date) - prediction_hours:]

    # Data preprocess
    scaler_train = MinMaxScaler(feature_range=(0, 1))
    scaled_train = scaler_train.fit_transform(df_train)
    scaler_test = MinMaxScaler(feature_range=(0, 1))
    scaled_test = scaler_test.fit_transform(df_test)

    trainX, trainY = dataset_generator_lstm(scaled_train)
    testX, testY = dataset_generator_lstm(scaled_test)

    trainX = np.reshape(trainX, (trainX.shape[0], trainX.shape[1], 5))
    testX = np.reshape(testX, (testX.shape[0], testX.shape[1], 5))

    # Build Model
    regressor = Sequential()
    regressor.add(LSTM(units=128, return_sequences=True, input_shape=(trainX.shape[1], trainX.shape[2])))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units=64, input_shape=(trainX.shape[1], trainX.shape[2])))
    regressor.add(Dropout(0.2))
    regressor.add(Dense(1))
    regressor.summary()

    # Compiling the LSTM
    regressor.compile(optimizer='adam', loss='mean_squared_error')

    checkpoint_path = 'Crypto_model/' + Crypto + '_model.hdf5'
    checkpoint = ModelCheckpoint(filepath=checkpoint_path, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
    earlystopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    callbacks = [checkpoint, earlystopping]

    regressor.fit(trainX, trainY, batch_size=32, epochs=20, verbose=1, shuffle=False, validation_data=(testX, testY), callbacks=callbacks)
