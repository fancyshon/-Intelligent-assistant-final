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

import tensorflow as tf

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.layers import LSTM
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

from FinMind.data import DataLoader


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


def Stock_model(Stock='2330'):
    # Get Data
    df = DataLoader().taiwan_stock_daily(stock_id=Stock, start_date='2012-01-01', end_date='2022-03-29')
    Stock_input_df = df
    Stock_input_df = Stock_input_df.set_index('date')
    Stock_input_df = Stock_input_df.sort_index()
    Stock_input_df = Stock_input_df.drop(['stock_id'], axis=1)
    Stock_input_df = Stock_input_df.drop(['spread'], axis=1)
    Stock_input_df = Stock_input_df.drop(['Trading_money'], axis=1)
    Stock_input_df = Stock_input_df.drop(['Trading_turnover'], axis=1)
    Stock_closing_price_groupby_date = Stock_input_df

    # Train Test Split
    prediction_hours = int(len(Stock_closing_price_groupby_date) * 0.2)
    df_train = Stock_closing_price_groupby_date.iloc[:len(Stock_closing_price_groupby_date) - prediction_hours]
    df_test = Stock_closing_price_groupby_date.iloc[len(Stock_closing_price_groupby_date) - prediction_hours:]

    # Data Preprocess
    scaler_train = MinMaxScaler(feature_range=(0, 1))
    scaled_train = scaler_train.fit_transform(df_train)

    scaler_test = MinMaxScaler(feature_range=(0, 1))
    scaled_test = scaler_test.fit_transform(df_test)

    trainX, trainY = dataset_generator_lstm(scaled_train)
    testX, testY = dataset_generator_lstm(scaled_test)

    trainX = np.reshape(trainX, (trainX.shape[0], trainX.shape[1], 5))
    testX = np.reshape(testX, (testX.shape[0], testX.shape[1], 5))

    # Create Model
    regressor = Sequential()
    regressor.add(LSTM(units=128, return_sequences=True, input_shape=(trainX.shape[1], trainX.shape[2])))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units=64, input_shape=(trainX.shape[1], trainX.shape[2])))
    regressor.add(Dropout(0.2))
    regressor.add(Dense(units=1))
    regressor.summary()

    regressor.compile(optimizer='adam', loss='mean_squared_error')

    checkpoint_path = 'Stock_model/' + Stock + '_model.hdf5'
    checkpoint = ModelCheckpoint(filepath=checkpoint_path, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
    earlystopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    callbacks = [checkpoint, earlystopping]

    history = regressor.fit(trainX, trainY, batch_size=32, epochs=20, verbose=1, shuffle=False, validation_data=(testX, testY), callbacks=callbacks)
