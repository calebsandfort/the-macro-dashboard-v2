# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 15:38:49 2022

@author: csandfort
"""
import os as os
import pandas as pd
import numpy as np
import json
import datetime
import dataRetrieval as dr
import assetClassesMfr as ac


def refreshData():
    allTickers = []
    
    temp = pd.read_csv(os.path.join(os.getcwd(), 'portfolios', "Portfolio.csv"), index_col="Ticker") 

    allTickers.extend(x for x in temp.index.values if x not in allTickers and x != 'Cash' and x != 'SDBA Cash')
    
    temp = pd.read_csv(os.path.join(os.getcwd(), 'portfolios', "MarketSnapshot.csv"), index_col="Ticker") 
    
    allTickers.extend(x for x in temp.index.values if x not in allTickers and x != 'Cash' and x != 'SDBA Cash')
    
    temp = pd.read_csv(os.path.join(os.getcwd(), 'portfolios', "Potentials.csv"), index_col="Ticker") 
    
    allTickers.extend(x for x in temp.index.values if x not in allTickers and x != 'Cash' and x != 'SDBA Cash')
    
    startDate = datetime.datetime.strptime('2019-05-01', '%Y-%m-%d')
    endDate = datetime.datetime.today()
    
    dr.GetTdaDataForTickers(allTickers, 'month', 'daily', 1, startDate, endDate, False, True)
    dr.GetAlphaQueryVolDataForTickers(allTickers)


# refreshData()

# portfolio = ac.AssetCollection("Test.csv")

# test = ac.AssetCollection("Potentials.csv")