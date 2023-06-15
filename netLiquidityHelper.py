# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 20:41:59 2022

@author: csandfort
"""
import datetime
import dataRetrieval as dr
import pandas as pd
import numpy as np


#C:/Users/csandfort/Source/Repos/TradingViewIndicatorGenerator/TradingViewIndicatorGenerator/CSVs/NetLiquidity

def getTheMostImportantData(refreshData = False, forVectorBt = False):
    
    startDate = datetime.datetime.strptime('2019-05-01', '%Y-%m-%d')
    endDate = datetime.datetime.today()
    spliceIndex = "2020-01-01"
    
    tga = dr.GetTreasuryData("TGA", startDate, endDate, refreshData)
    # tga = tga[spliceIndex:]
    
    fredData = dr.GetFredDataForTickers(["FED", "RRP"], startDate, endDate, refreshData)
    fed = fredData["FED"]
    rrp = fredData["RRP"]
    
    if refreshData:
        dr.GetTdaDataForTickers(["SPY"], 'month', 'daily', 1, startDate, endDate, False, True)
    
    rawData, v = dr.GetDataFromCsv(["SPY"], getVolData = False)
    
    spx = rawData["SPY"]
    # btc = rawData["BTC"]
    
    masterIndex = spx.index.values[-800 if forVectorBt else -400:]
    fedIndex = fed.index.values
    rrpIndex = rrp.index.values
    spxIndex = spx.index.values
    # btcIndex = btc.index.values
    
    for idx in masterIndex:
        if (idx not in fedIndex):
            fed.at[idx, "value"] = np.NaN
            
        if (idx not in rrpIndex):
            rrp.at[idx, "value"] = np.NaN
            
        if (idx not in spxIndex):
            spx.at[idx, "close"] = np.NaN
            
        # if (idx not in btcIndex):
        #     btc.at[idx, "close"] = np.NaN
    
    tga.sort_index(inplace=True)
    tga.fillna(method="ffill", inplace=True)
    
    fed.sort_index(inplace=True)
    fed.fillna(method="ffill", inplace=True)
    # fed = fed[spliceIndex:]
    
    rrp.sort_index(inplace=True)
    rrp.fillna(method="ffill", inplace=True)
    # rrp = rrp[spliceIndex:]
    
    spx.sort_index(inplace=True)
    spx.fillna(method="ffill", inplace=True)
    # spx = spx[spliceIndex:]
    
    # btc.sort_index(inplace=True)
    # btc.fillna(method="ffill", inplace=True)
    # btc = btc[spliceIndex:]
    
    data = pd.DataFrame(index = masterIndex)
    data.index.name='date'
    data["fed"] = fed["value"]
    data["fed"].fillna(method="ffill", inplace=True)
    data["fed"] = data["fed"].shift()
    data["fed"].fillna(method="bfill", inplace=True)
    data["tga"] = tga["value"]
    data["tga"].fillna(method="ffill", inplace=True)
    data["tga"] = data["tga"].shift()
    data["tga"].fillna(method="bfill", inplace=True)
    data["rrp"] = rrp["value"]
    data["rrp"].fillna(method="ffill", inplace=True)
    data["netLiquidity"] = fed["value"] - data["tga"] - rrp["value"]
    data["netLiquidity"].fillna(method="bfill", inplace=True)
    
    if forVectorBt:       
        data.to_csv("C:/Users/csandfort/Documents/Python Scripts/Backtesting/VectorBtPro/NetLiquidity.csv")
    else:
        data.to_csv("C:/Users/csandfort/Source/Repos/TradingViewIndicatorGenerator/TradingViewIndicatorGenerator/CSVs/NetLiquidity/netLiquidity.csv")

    return data
    
    
test = getTheMostImportantData(True, False)