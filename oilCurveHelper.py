# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 15:21:36 2022

@author: csandfort
"""
import dataRetrieval as dr
import os as os
import pandas as pd
import datetime

def constructCurve(refreshData = False):
    contractsTable = pd.read_csv(os.path.join(os.getcwd(), 'data', "OilContractsTable.csv"), index_col="Month")
    
    contractTickers = []
    curveDfIndex = []
    years = contractsTable.columns[1:]
    
    for year in years:
        for month in contractsTable.index.values:
            if contractsTable.at[month, f'{year}'] == "yes":
                contractTickers.append(f"CL{contractsTable.at[month, 'Code']}{year.replace('20', '')}.NYM")
                curveDfIndex.append(datetime.datetime(int(year), int(month), 27))
                
                
    startDate = datetime.datetime.today() - datetime.timedelta(days=365)
    endDate = datetime.datetime.today()
    
    if refreshData:
        dr.GetTdaDataForTickers(contractTickers, 'month', 'daily', 1, startDate, endDate, False, True)
    
    rawData, v = dr.GetDataFromCsv(contractTickers, getVolData = False)
    
    rateData = {}
    
    for key in rawData:
        rateData[key] = pd.DataFrame(index = rawData[key].index.values)
        rateData[key]["rate"] = rawData[key]["close"]


    curveDf = pd.DataFrame(index = curveDfIndex)
    
    
    curveDf["today"] = getRateColumn(contractTickers, rateData, 0)
    curveDf["1D"] = getRateColumn(contractTickers, rateData, 1)
    curveDf["1W"] = getRateColumn(contractTickers, rateData, 5)
    curveDf["1M"] = getRateColumn(contractTickers, rateData, 21)

    return curveDf

def getRateColumn(contractTickers, rateData, shift):
    col = []
    
    for contractTicker in contractTickers:
        col.append(rateData[contractTicker]["rate"].shift(shift).values[-1])

    return col

# d = constructCurve()

            
# jan23 = datetime.datetime.strptime('2023-01-31', '%Y-%m-%d')
# feb23 = jan23 + relativedelta(months=13)

# TODO
# 1. Create index by looping thru contracts in and creating date object for last day of year/month combo
# 2. Loops thru contracts in chronological order and take last rate value and add it to list
# 3. Add column to dataframe for above list
# 4. Complete steps 2/3 for today, 1D, 1W, 1M
# 5. Find suitable color pallete
# 6. Add tab and chart each column 