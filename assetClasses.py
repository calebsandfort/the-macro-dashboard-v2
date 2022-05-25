# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 15:41:16 2022

@author: csandfort
"""

import os as os
import pandas as pd
import numpy as np
import json
import datetime
import dataRetrieval as dr
import technicals

class Asset:
    def __init__(self, ticker, quantity = 0.0, entry = 0.0, corrTicker = "", j = None):
        if j is None:
            self.id = ticker
            self.ticker = ticker
            self.quantity = quantity
            self.entry = entry
            self.cost_basis = self.quantity * self.entry

            self.corrTicker = "" if corrTicker == "nil" else corrTicker
            
            self.price_data = None
            self.vol_data = None
            self.last = 0.0
            
            #Chg
            self.Chg1D = 0.0
            self.Chg1M = 0.0
            self.Chg3M = 0.0
            
            #Trend/Trade
            self.Trend = 0.0
            self.Trade = 0.0
            self.IsBullTrend = False
            self.IsBullTrade = False
            self.TrendEmoji = '😀'
            self.TradeEmoji = '😀'
            
            #BridgeBands
            self.BBPos = 0.0
            
            #Volume
            self.VolumeDesc = "None"
            
            #Volatility
            self.IvPd = 0.0
            self.IV1DΔ = 0.0
            self.IV1WΔ = 0.0
            self.IV1MΔ = 0.0
            
        else:
            self.__dict__ = json.loads(j)
       
   
    @property
    def df_row(self):
        return [self.id, self.ticker, self.quantity, self.entry, self.last, self.Chg1D, self.Chg1M, self.Chg3M, self.Trend, self.Trade,
                self.IsBullTrend, self.IsBullTrade, self.TrendEmoji, self.TradeEmoji, self.BBPos, self.VolumeDesc, self.IvPd,
                self.IV1DΔ, self.IV1WΔ, self.IV1MΔ] 
       
    def toJson(self):
        d = self.__dict__.copy()
        d.pop("price_data", None)
        
        return json.dumps(d);

    
    def setDataAndTechnicals(self, price_data, vol_data):
        self.price_data = price_data
        self.vol_data = vol_data
        
        self.last = self.price_data.at[self.price_data.index[-1], "close"]
        self.price_data["IsUp"] = self.price_data['close'] > self.price_data['close'].shift(1)
    
        #%% Chg
        self.price_data['Chg1D'] = (self.price_data['close'] / self.price_data['close'].shift(1)) - 1.0
        self.Chg1D = self.price_data.at[self.price_data.index[-1], "Chg1D"]
        
        self.price_data['Chg1M'] = (self.price_data['close'] / self.price_data['close'].shift(21)) - 1.0
        self.Chg1M = self.price_data.at[self.price_data.index[-1], "Chg1M"]
        
        self.price_data['Chg3M'] = (self.price_data['close'] / self.price_data['close'].shift(63)) - 1.0
        self.Chg3M = self.price_data.at[self.price_data.index[-1], "Chg3M"]
        #%%
        
        #%% Trend/Trade       
        trend, outlook = technicals.getTrend(self.price_data, 'low', 'high', 'close', 63)
        self.price_data['Trend'] = trend
        self.Trend = self.procureLastValue("Trend")
        
        trade, trade_outlook = technicals.getTrend(self.price_data, 'low', 'high', 'close', 21)
        self.price_data['Trade'] = trade
        self.Trade = self.procureLastValue("Trade")
        
        self.price_data["IsBullTrend"] = self.price_data["close"] > self.price_data["Trend"]
        self.IsBullTrend = self.procureLastValue("IsBullTrend")
        
        self.price_data['TrendEmoji'] = self.price_data['IsBullTrend'].apply(lambda x: '✔️' if x else '❌')
        self.TrendEmoji = self.procureLastValue("TrendEmoji")
        
        self.price_data["BullTrend"] = self.price_data["Trend"]
        self.price_data.loc[(self.price_data['IsBullTrend'] == False), 'BullTrend'] = None

        self.price_data["BearTrend"] = self.price_data["Trend"]
        self.price_data.loc[(self.price_data['IsBullTrend'] == True), 'BearTrend'] = None
        
        self.price_data["IsBullTrade"] = self.price_data["close"] > self.price_data["Trade"]
        self.IsBullTrade = self.procureLastValue("IsBullTrade")
        
        self.price_data['TradeEmoji'] = self.price_data['IsBullTrade'].apply(lambda x: '✔️' if x else '❌')
        self.TradeEmoji = self.procureLastValue("TradeEmoji")
        
        self.price_data["BullTrade"] = self.price_data["Trade"]
        self.price_data.loc[(self.price_data['IsBullTrade'] == False), 'BullTrade'] = None

        self.price_data["BearTrade"] = self.price_data["Trade"]
        self.price_data.loc[(self.price_data['IsBullTrade'] == True), 'BearTrade'] = None
        
        #%%
                
        #%% BridgeBands
        BridgeBandBottom, BridgeBandTop = technicals.BridgeBands(self.price_data, self.price_data.close, 15)
        self.price_data['BBBot'] = BridgeBandBottom
        self.price_data['BBTop'] = BridgeBandTop
        
        self.price_data['BBPos'] = (BridgeBandTop - self.price_data['close']) / (BridgeBandTop - BridgeBandBottom)
        self.price_data.loc[(self.price_data['BBPos'] > 1.), 'BBPos'] = 1.0
        self.price_data.loc[(self.price_data['BBPos'] < 0.), 'BBPos'] = 0.0
        self.BBPos = self.procureLastValue("BBPos")
        
        #%%
        
        #%% Volume
        self.price_data = technicals.calcVolumeMetrics(self.price_data)
        
        self.price_data.loc[(self.price_data['VolumeEnum'] == 0.0) & (self.price_data["IsUp"] == True), 'VolumeDesc'] = 'Weak'
        self.price_data.loc[(self.price_data['VolumeEnum'] == 1.0) & (self.price_data["IsUp"] == True), 'VolumeDesc'] = 'Moderate'
        self.price_data.loc[(self.price_data['VolumeEnum'] == 2.0) & (self.price_data["IsUp"] == True), 'VolumeDesc'] = 'Strong'
        self.price_data.loc[(self.price_data['VolumeEnum'] == 3.0) & (self.price_data["IsUp"] == True), 'VolumeDesc'] = 'Absolute'
        
        self.price_data.loc[(self.price_data['VolumeEnum'] == -0.0) & (self.price_data["IsUp"] == False), 'VolumeDesc'] = 'Weak'
        self.price_data.loc[(self.price_data['VolumeEnum'] == -1.0) & (self.price_data["IsUp"] == False), 'VolumeDesc'] = 'Moderate'
        self.price_data.loc[(self.price_data['VolumeEnum'] == -2.0) & (self.price_data["IsUp"] == False), 'VolumeDesc'] = 'Strong'
        self.price_data.loc[(self.price_data['VolumeEnum'] == -3.0) & (self.price_data["IsUp"] == False), 'VolumeDesc'] = 'Absolute'
        
        self.VolumeDesc = self.price_data.at[self.price_data.index[-1], "VolumeDesc"]
        #%%
        
        #%% Volatility
        self.vol_data['IvPd'] = (self.vol_data['IvPut30'] / ((self.vol_data['Hv10'] + self.vol_data['Hv20'] + self.vol_data['Hv30']) / 3.0)) - 1.0
        self.IvPd = self.procureLastVolValue("IvPd")
        
        self.vol_data['IV1DΔ'] = (self.vol_data['IvPd'].shift(1) - self.vol_data['IvPd'])
        self.IV1DΔ = self.procureLastVolValue("IV1DΔ")
                      
        self.vol_data['IV1WΔ'] = (self.vol_data['IvPd'].shift(5) - self.vol_data['IvPd'])
        self.IV1WΔ = self.procureLastVolValue("IV1WΔ")
               
        self.vol_data['IV1MΔ'] = (self.vol_data['IvPd'].shift(21) - self.vol_data['IvPd'])
        self.IV1MΔ = self.procureLastVolValue("IV1MΔ")
        #%%
        
    def procureLastValue(self, col):
        return self.price_data.at[self.price_data.index[-1], col]
    
    def procureLastVolValue(self, col):
        return self.vol_data.at[self.vol_data.index[-1], col]
    
class AssetCollection:
    def __init__(self, csvFileName = None, existing = None, refreshData = False):
        self.collection = {}
        
        
        if csvFileName is not None:
            temp = pd.read_csv(os.path.join(os.getcwd(), 'portfolios', csvFileName), index_col="Ticker") 
            
            for ticker in temp.index.values:
                self.collection[ticker] = Asset(ticker, temp.at[ticker, 'Quantity'], temp.at[ticker, 'Entry'])
                
            if "SDBA Cash" in self.collection.keys():
                self.collection["Cash"].entry += self.collection["SDBA Cash"].entry
                self.collection["Cash"].last = self.collection["Cash"].entry
                del self.collection['SDBA Cash']
        else:
            for ticker in existing:
                self.collection[ticker] = Asset(ticker, j = existing[ticker])
                
        self.df = pd.DataFrame(columns = ["id", "Ticker", "Quantity", "Entry", "Last", "Chg1D", "Chg1M", "Chg3M", "Trend", "Trade",
                                          "IsBullTrend", "IsBullTrade", "TrendEmoji", "TradeEmoji", "BBPos", "VolumeDesc", "IvPd",
                                          "IV1DΔ", "IV1WΔ", "IV1MΔ"])
        
        self.df.loc["Cash"] = self.collection["Cash"].df_row
        
        startDate = datetime.datetime.strptime('2019-05-01', '%Y-%m-%d')
        endDate = datetime.datetime.today()
        allTickers = [ticker for ticker in self.collection]
        allTickers.remove("Cash")
        price_data, vol_data = dr.GetDataFromCsv(allTickers)
        
        for ticker in allTickers:
            if ticker != "Cash":
                self.collection[ticker].setDataAndTechnicals(price_data[ticker], vol_data[ticker])
                self.df.loc[ticker] = self.collection[ticker].df_row
             
        
        self.df["Cost Basis"] = self.df["Quantity"] * self.df["Entry"]
        self.df["Current Value"] = self.df["Quantity"] * self.df["Last"]
        self.df["Weight"] = self.df["Current Value"] / self.df["Current Value"].sum()
        self.df["PnL"] = ((self.df["Last"] - self.df["Entry"]) / self.df["Entry"])
        
        # print(self.df.head())
        
        self.portfolio_value = 0.0
                
    def toDict(self):
        temp = {}
        
        for ticker in self.collection:
            temp[ticker] = self.collection[ticker].toJson();

        return temp

#blah = AssetCollection("Portfolio.csv")

# d = blah.toDict()

# blah2 = AssetCollection(existing = d)

#jsonStr = json.dumps(blah.__dict__)