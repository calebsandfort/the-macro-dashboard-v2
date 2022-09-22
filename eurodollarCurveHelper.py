# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 15:21:36 2022

@author: csandfort
"""
import dataRetrieval as dr
import pandas as pd
import datetime

import yfinance as yf 

contractYears = [22, 23, 24, 25, 26, 27, 28, 29, 30 ]
monthDays = {
    "F": 31, "G": 28, "H": 31, "J": 30, "K": 31, "M": 30, "N": 31, "Q": 31, "U": 30, "V": 31, "X": 30, "Z": 31 
    }
monthCodes = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z" ]
activeTickers = ['GEU22.CME', 'GEV22.CME', 'GEX22.CME', 'GEZ22.CME', 'GEF23.CME', 'GEH23.CME', 'GEM23.CME', 'GEU23.CME', 'GEZ23.CME', 'GEH24.CME', 'GEM24.CME', 'GEU24.CME', 'GEZ24.CME', 'GEH25.CME', 'GEM25.CME', 'GEU25.CME', 'GEZ25.CME', 'GEH26.CME', 'GEM26.CME', 'GEU26.CME', 'GEZ26.CME', 'GEH27.CME', 'GEM27.CME', 'GEU27.CME', 'GEZ27.CME', 'GEH28.CME', 'GEM28.CME', 'GEU28.CME', 'GEZ28.CME', 'GEH29.CME', 'GEM29.CME', 'GEU29.CME', 'GEZ30.CME']

def constructCurve(refreshData = False):

    curveDfIndex = []

    for activeTicker in activeTickers:
         monthCode = activeTicker[2]
         monthInt = monthCodes.index(monthCode) + 1
         dayCount = monthDays[monthCode]
         year = 2000 + int(activeTicker.replace(".CME", "")[-2:])
         
         curveDfIndex.append(datetime.datetime(year, monthInt, dayCount))
       
                
    startDate = datetime.datetime.today() - datetime.timedelta(days=365)
    endDate = datetime.datetime.today()
    
    if refreshData:
        dr.GetTdaDataForTickers(activeTickers, 'month', 'daily', 1, startDate, endDate, False, True)
    
    rawData, v = dr.GetDataFromCsv(activeTickers, getVolData = False)
    
    rateData = {}
    
    for key in rawData:
        rateData[key] = pd.DataFrame(index = rawData[key].index.values)
        rateData[key]["rate"] = 100.0 - rawData[key]["close"]


    curveDf = pd.DataFrame(index = curveDfIndex)
    
    
    curveDf["today"] = getRateColumn(activeTickers, rateData, 0)
    curveDf["1D"] = getRateColumn(activeTickers, rateData, 1)
    curveDf["1W"] = getRateColumn(activeTickers, rateData, 5)
    curveDf["1M"] = getRateColumn(activeTickers, rateData, 21)

    return curveDf

def getRateColumn(contractTickers, rateData, shift):
    col = []
    
    for contractTicker in contractTickers:
        col.append(rateData[contractTicker]["rate"].shift(shift).values[-1])

    return col



def constructCurveDynamically(refreshData = False):
    
    sym = ""
    info = None
    
    contractTickers = []

    for contractYear in contractYears:
        for monthCode in monthCodes:
            sym = f"GE{monthCode}{contractYear}.CME"
            contractTickers.append(sym)
       
    allTickers = yf.Tickers(' '.join(contractTickers))
    
    contractTickers = []
    curveDfIndex = []
    
    for key in allTickers.tickers:
        if len(allTickers.tickers[key].info.keys()) > 5:
            contractTickers.append(key)

    
    print(",".join(contractTickers))

    # years = contractsTable.columns[1:]
    
    # for year in years:
    #     for month in contractsTable.index.values:
    #         if contractsTable.at[month, f'{year}'] == "yes":
    #             contractTickers.append(f"GE{contractsTable.at[month, 'Code']}{year.replace('20', '')}.CME")
    #             curveDfIndex.append(datetime.datetime(int(year), int(month), 27))
                
                
    # startDate = datetime.datetime.today() - datetime.timedelta(days=365)
    # endDate = datetime.datetime.today()
    
    # if refreshData:
    #     dr.GetTdaDataForTickers(contractTickers, 'month', 'daily', 1, startDate, endDate, False, True)
    
    # rawData, v = dr.GetDataFromCsv(contractTickers, getVolData = False)
    
    # rateData = {}
    
    # for key in rawData:
    #     rateData[key] = pd.DataFrame(index = rawData[key].index.values)
    #     rateData[key]["rate"] = 100.0 - rawData[key]["close"]


    # curveDf = pd.DataFrame(index = curveDfIndex)
    
    
    # curveDf["today"] = getRateColumn(contractTickers, rateData, 0)
    # curveDf["1D"] = getRateColumn(contractTickers, rateData, 1)
    # curveDf["1W"] = getRateColumn(contractTickers, rateData, 5)
    # curveDf["1M"] = getRateColumn(contractTickers, rateData, 21)

    # return curveDf
    
    return "test"

def getActiveTickers():
    sym = ""
    contractTickers = []
    
    for contractYear in contractYears:
        for monthCode in monthCodes:
            sym = f"GE{monthCode}{contractYear}.CME"
            contractTickers.append(sym)
       
    allTickers = yf.Tickers(' '.join(contractTickers))
    
    contractTickers = []
    
    for key in allTickers.tickers:
        
        k = len(allTickers.tickers[key].info.keys())
        
        if (k > 5):
            contractTickers.append(key)

    
    print("', '".join(contractTickers))

# test = yf.Ticker("GEF22.CME")
# l = len(test.info.keys()) > 5

# getActiveTickers()

# d = constructCurveDynamically()

            
# jan23 = datetime.datetime.strptime('2023-01-31', '%Y-%m-%d')
# feb23 = jan23 + relativedelta(months=13)

# TODO
# 1. Create index by looping thru contracts in and creating date object for last day of year/month combo
# 2. Loops thru contracts in chronological order and take last rate value and add it to list
# 3. Add column to dataframe for above list
# 4. Complete steps 2/3 for today, 1D, 1W, 1M
# 5. Find suitable color pallete
# 6. Add tab and chart each column 