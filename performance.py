# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 16:16:27 2022

@author: csandfort
"""
import pandas as pd
import numpy as np
from numpy import sqrt
import dataRetrieval as dr
import json

def getPortfolioAndBenchmarksPerformanceDict():
    rawCsv = pd.read_csv("portfolios/PerformanceData.csv", index_col="datetime", parse_dates=True, dtype={"composite": float})
    startDate = rawCsv.index.values[0]
    endDate = rawCsv.index.values[-1]
    
    tda_data, vol_data = dr.GetDataFromCsv(["RFR"], False)
    rfr = tda_data["RFR"][startDate:endDate]["close"]
    
    portfolioAndBenchmarksPerformanceDict = {}
    
    portfolioAndBenchmarksPerformanceDict["Portfolio"] = getPerformanceDf(rawCsv, rfr)
    
    with open('portfolios/Benchmarks.txt') as f:
        data = f.read()

    benchmarksDictFromJson = json.loads(data)
    
    for key in benchmarksDictFromJson:
        composite = buildBenchmarkComposite(benchmarksDictFromJson[key], startDate, endDate)
        portfolioAndBenchmarksPerformanceDict[key] = getPerformanceDf(composite, rfr)
    
    
    return portfolioAndBenchmarksPerformanceDict

def buildBenchmarkComposite(benchmarkDict, startDate, endDate):
    
    idxVals = None
    
    datii = []
    
    for ticker in benchmarkDict["Tickers"]:
        tda_data, vol_data = dr.GetDataFromCsv([ticker], False)
        
        if idxVals is None:
            idxVals = tda_data[ticker][startDate:endDate].index.values
        
        datii.append(tda_data[ticker][startDate:endDate]["close"])


    df = pd.DataFrame(index = idxVals)   
    df["composite"] = 0.0
    
    for i in range(0, len(datii)):
        df["composite"] = df["composite"] + (datii[i] * benchmarkDict["Weights"][i])
        
    return df

def allTimePerformance(x, start):
    return (x-start)/start

def deltaDays(x, start):
    return (x-start).days

def getPerformanceDf(data, rfr):
    data["Date"] = data.index.values
    startDate = data.index.values[0]
    endDate = data.index.values[-1]
    startValue = data.at[data.index[0], 'composite']
    
    tda_data, vol_data = dr.GetDataFromCsv(["RFR"], False)
    rfr = tda_data["RFR"][startDate:endDate]["close"]
    
    
    performanceDf = pd.DataFrame(index = data.index)
    idx_values = performanceDf.index.values
    
    performanceDf["Value"] = data['composite']
    
    performanceDf["DailyPerformance"] = (data['composite'] / data['composite'].shift(1)) - 1.0
    performanceDf['DailyPerformance'] = performanceDf['DailyPerformance'].fillna(0.0)
    
    
    performanceDf["AllTimePerformance"] = data['composite'].apply(allTimePerformance, start = startValue)
    
    DR_RF = performanceDf['DailyPerformance'] - ((1.0 + rfr / 100.0) ** (1/252) - 1.0)
    Diff_DR_DF_Avg = (DR_RF - performanceDf['DailyPerformance'].expanding().mean()) ** 2

    performanceDf["SharpeRatio"] = (DR_RF.expanding().mean()) / (sqrt(Diff_DR_DF_Avg.expanding().sum() / (Diff_DR_DF_Avg.expanding().count() - 1.0))) * 15.8745
    
    performanceDf["DDownsideRisk"] = np.select([DR_RF < 0], [(DR_RF - DR_RF.expanding().mean()) ** 2], np.NaN)
    
    performanceDf["SortinoRatio"] = (DR_RF.expanding().mean()) / (sqrt(performanceDf["DDownsideRisk"].expanding().sum() / (performanceDf["DDownsideRisk"].expanding().count()))) * 15.8745
    
    performanceDf["PeakEquity"] = data["composite"]
    
    for i in range(1, len(idx_values)):
        t = performanceDf.at[idx_values[i], "PeakEquity"]
        t_minus_1 = performanceDf.at[idx_values[i - 1], "PeakEquity"]
        
        if t > t_minus_1:
            performanceDf.at[idx_values[i], "PeakEquity"] = t
        else:
            performanceDf.at[idx_values[i], "PeakEquity"] = t_minus_1
    
    
    
    performanceDf["CAGR"] = pow(data["composite"] / startValue, 1.0 / (data['Date'].apply(deltaDays, start = startDate) / 365.0)) - 1.0
    
    
    performanceDf["DrawdownValue"] = 0.0
    
    for i in range(1, len(idx_values)):
        composite_t = data.at[idx_values[i], "composite"]
        
        peak_equity_t = performanceDf.at[idx_values[i], "PeakEquity"]
        peak_equity_t_minus_1 = performanceDf.at[idx_values[i - 1], "PeakEquity"]
        
        if composite_t < peak_equity_t:
            performanceDf.at[idx_values[i], "DrawdownValue"] = composite_t - peak_equity_t_minus_1  
    
    
    performanceDf["DrawdownPtg"] = 0.0
    
    for i in range(1, len(idx_values)):
        drawdown_value_t = performanceDf.at[idx_values[i], "DrawdownValue"]
        peak_equity_t = performanceDf.at[idx_values[i], "PeakEquity"]
        
        if drawdown_value_t != 0.0:
            performanceDf.at[idx_values[i], "DrawdownPtg"] = -drawdown_value_t/peak_equity_t
    
    
    performanceDf["CalmarRatio"] = performanceDf["CAGR"] / performanceDf["DrawdownPtg"].expanding().max()
    
    performanceDf.at[idx_values[0], "CalmarRatio"] = 0.0
    
    
    
    performanceDf["GainPainRatio"] = 0.0
    
    total_return = 0.0
    pain_return = 0.0
    
    for i in range(1, len(idx_values)):
        daily_return = performanceDf.at[idx_values[i], "DailyPerformance"]
        
        total_return += daily_return
        
        if daily_return < 0.0:
            pain_return += abs(daily_return)
        
        if pain_return != 0.0:
            performanceDf.at[idx_values[i], "GainPainRatio"] = total_return / pain_return   
    
    
    performanceDf.replace([np.inf, -np.inf, -0.0], 0, inplace=True)
    performanceDf = performanceDf.round({"DailyPerformance": 4, "AllTimePerformance": 4,
                                         "SharpeRatio": 2, "SortinoRatio": 2, "CAGR": 4,
                                         "CalmarRatio": 2, "GainPainRatio": 2})
    
    return performanceDf;

def getPerformanceStatsDict(performanceStatsDf):
    performanceStatsDict = {}
    
    lastIdx = performanceStatsDf.index.values[-1]
    
    performanceStatsDict["Value"] = performanceStatsDf.at[lastIdx, "Value"]
    performanceStatsDict["PnL"] = performanceStatsDf.at[lastIdx, "AllTimePerformance"]
    performanceStatsDict["MaxDrawdown"] = performanceStatsDf["DrawdownPtg"].max()
    performanceStatsDict["AvgDailyPnL"] = performanceStatsDf["DailyPerformance"].mean()
    performanceStatsDict["CurrentDrawdown"] = performanceStatsDf.at[lastIdx, "DrawdownPtg"]
    performanceStatsDict["PeakEquity"] = performanceStatsDf["PeakEquity"].max()
    performanceStatsDict["SharpeRatio"] = performanceStatsDf.at[lastIdx, "SharpeRatio"]
    performanceStatsDict["SortinoRatio"] = performanceStatsDf.at[lastIdx, "SortinoRatio"]
    performanceStatsDict["CalmarRatio"] = performanceStatsDf.at[lastIdx, "CalmarRatio"]
    performanceStatsDict["GainPainRatio"] = performanceStatsDf.at[lastIdx, "GainPainRatio"]
    
    return performanceStatsDict

# test = getPortfolioAndBenchmarksPerformanceDict()
