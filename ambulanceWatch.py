# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 16:47:42 2022

@author: csandfort
"""
# import investpy

# df = investpy.get_stock_historical_data(stock='AAPL',
#                                         country='United States',
#                                         from_date='01/01/2010',
#                                         to_date='01/01/2020')
# print(df.head())

import datetime
import dataRetrieval as dr
import pandas as pd
import numpy as np

def getTheMostImportantData(refreshData = False):
    
    startDate = datetime.datetime.strptime('2019-05-01', '%Y-%m-%d')
    endDate = datetime.datetime.today()
    spliceIndex = "2021-01-01"
    
    tga = dr.GetTreasuryData("TGA", startDate, endDate, refreshData)
    tga = tga[spliceIndex:]
    
    fredData = dr.GetFredDataForTickers(["FED", "RRP"], startDate, endDate, refreshData)
    fed = fredData["FED"]
    rrp = fredData["RRP"]
    
    if refreshData:
        dr.GetTdaDataForTickers(["ES", "BTC"], 'month', 'daily', 1, startDate, endDate, False, True)
    
    rawData, v = dr.GetDataFromCsv(["ES", "BTC"], getVolData = False)
    
    es = rawData["ES"]
    btc = rawData["BTC"]
    
    masterIndex = tga.index.values
    fedIndex = fed.index.values
    rrpIndex = rrp.index.values
    esIndex = es.index.values
    btcIndex = btc.index.values
    
    for idx in masterIndex:
        if (idx not in fedIndex):
            fed.at[idx, "value"] = np.NaN
            
        if (idx not in rrpIndex):
            rrp.at[idx, "value"] = np.NaN
            
        if (idx not in esIndex):
            es.at[idx, "close"] = np.NaN
            
        if (idx not in btcIndex):
            btc.at[idx, "close"] = np.NaN
    
    
    
    fed.sort_index(inplace=True)
    fed.fillna(method="ffill", inplace=True)
    fed = fed[spliceIndex:]
    
    rrp.sort_index(inplace=True)
    rrp.fillna(method="ffill", inplace=True)
    rrp = rrp[spliceIndex:]
    
    es.sort_index(inplace=True)
    es.fillna(method="ffill", inplace=True)
    es = es[spliceIndex:]
    
    btc.sort_index(inplace=True)
    btc.fillna(method="ffill", inplace=True)
    btc = btc[spliceIndex:]
    
    data = pd.DataFrame(index = masterIndex)
    data["netLiquidity"] = fed["value"] - tga["value"] - rrp["value"]
    data["es"] = es["close"]
    data["btc"] = btc["close"]

    return data
    
    
test = getTheMostImportantData(True)
    
    
    