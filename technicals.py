# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 13:42:09 2021

@author: csandfort
"""
import numpy as np
import pandas as pd
import math
from operator import add 
from finta import TA

def calcHv(data, window):
    log_returns = np.log(data['close'] / data['close'].shift())
    return log_returns.rolling(window).std()*252**.5

def calcHvMean(data):
    hv30 = calcHv(data, 21)
    hv20 = calcHv(data, 14)
    hv10 = calcHv(data, 7)
    
    return (hv30 + hv20 + hv10) / 3.0

def calcHvZScore(data, window):
    hvMean = calcHvMean(data)
    mean = hvMean.rolling(window=window).mean()
    std = hvMean.rolling(window=window).std()

    return (hvMean - mean)/std

def calcZScore(data, col, window = None, is_negative = False):
    col_values = data[col]
    
    if is_negative:
        col_values = col_values * -1.0
    
    mean = None
    std = None
    
    if window is None:
        mean = col_values.mean()
        std = col_values.std()
    else:
        mean = col_values.rolling(window=window).mean()
        std = col_values.rolling(window=window).std()

    return (col_values - mean)/std

def getTrend(data, lowColumn, highColumn, closeColumn, period): 
     lowestLow = data[lowColumn].rolling(period).min();
     highestHigh = data[highColumn].rolling(period).max();
        
     trend = pd.Series(lowestLow + ((highestHigh - lowestLow) / 2)) 
     outlook = [.5] * len(trend)
    
     for i in range(1, len(trend)):
       if trend.iloc[i] < data[closeColumn].iloc[i] and trend.iloc[i - 1] < data[closeColumn].iloc[i - 1]:
         outlook[i] = 1.0
       elif trend.iloc[i] > data[closeColumn].iloc[i] and trend.iloc[i - 1] > data[closeColumn].iloc[i - 1]:
         outlook[i] = 0.
            
     return trend, outlook
 
def Hurst(data, length):
    logLength = math.log(length)
    
    highest = data['high'].rolling(length).max()
    lowest = data['low'].rolling(length).min()
    atr = TA.ATR(data, length)
    logAtr = np.log(atr)
    
    h = (np.log(highest - lowest) - logAtr) / logLength
    
    return h;

def BridgeRanges(src, n):
  slopes = ((src - src.shift(n - 1)) / (n - 1)).tolist()

  srcList = src.tolist()
  srcList.reverse()
  slopes.reverse()
  MinDiffs = [0] * len(srcList)
  MaxDiffs = [0] * len(srcList)
    
  nMinus1 = n - 1
  s = 0
  min_diff = 0.0
  max_diff = 0.0
    
  for index in range(len(srcList) - n):
    min_diff = 100000000.0
    max_diff = -100000000.0
    s = slopes[index]
    subset = srcList[index : index + n]

    for i in range(n):
      min_diff = min(min_diff, subset[nMinus1 - i] - (subset[nMinus1] + (s * i)))
      max_diff = max(max_diff, subset[nMinus1 - i] - (subset[nMinus1] + (s * i)))
        
    MinDiffs[index] = min_diff
    MaxDiffs[index] = max_diff

  srcList.reverse()
  MinDiffs.reverse()
  MaxDiffs.reverse()
    
  BridgeRangeBottom = list(map(add, srcList, MinDiffs))
  BridgeRangeTop = list(map(add, srcList, MaxDiffs))
  
  return BridgeRangeBottom, BridgeRangeTop

def BridgeBands(d, src, n):
    
    
    BridgeRangeBottom, BridgeRangeTop = BridgeRanges(d.close, 15)
    
    hurst = Hurst(d, n)
    
    bbands = TA.BBANDS(d, 15, TA.WMA(d, 15))
    bb_bottom = bbands['BB_LOWER']
    bb_top = bbands['BB_UPPER']
    
    BridgeBandBottom = bb_bottom + ((BridgeRangeBottom - bb_bottom) * abs((hurst * 2) - 1))
    BridgeBandTop = bb_top - ((bb_top - BridgeRangeTop) * abs((hurst * 2) - 1))
    
    return BridgeBandBottom, BridgeBandTop

def calcVolumeMetrics(data):
    data["Volume1W"] = data["volume"].rolling(5).mean()
    data["Volume1M"] = data["volume"].rolling(21).mean()
    
    data["VolumeEnum"] = len(data) * .01
    
    previousIndex = None
    ydayVolume = 0.0
    todayVolume = 0.0
    weekVolume = 0.0
    monthVolume = 0.0
    
    for idx in data.index.values:
        if previousIndex is None:
            data.at[idx, "VolumeEnum"] = 0.0
            previousIndex = idx
        else:
            volumeEnum = 0.0
            
            todayVolume = data.at[idx, "volume"]
            ydayVolume = data.at[previousIndex, "volume"]
            weekVolume = data.at[idx, "Volume1W"]
            monthVolume = data.at[idx, "Volume1M"]
            
            if todayVolume > ydayVolume: volumeEnum = volumeEnum + 1.0
            if todayVolume > weekVolume: volumeEnum = volumeEnum + 1.0
            if todayVolume > monthVolume: volumeEnum = volumeEnum + 1.0
            
            data.at[idx, "VolumeEnum"] = volumeEnum * (1.0 if data.at[idx, "close"] > data.at[previousIndex, "close"] else -1.0)
            
            # print(data.at[idx, "VolumeEnum"], "     ", idx)
            
            previousIndex = idx
    
    return data

def CCI(df, ndays): 
    tp = df['close']
    sma = tp.rolling(ndays).mean()
    mad = tp.rolling(ndays).apply(lambda x: pd.Series(x).mad(), raw=False)
    cci = (tp - sma) / (0.015 * mad) 
    
    return cci

def calcMatrix(data):
    nn = 5
    
    # Sup/Res Detail
    SupResPeriod = 50
    SupResPercentage = 100
    PricePeriod = 16
    ob = 200
    os = -200

    pd = 22
    bbl = 20
    mult = 2.0
    lb = 50
    ph = .85
    
    ltLB = 40
    mtLB = 14
    _str = 3
    
    swvfm = 1
    
    # Williams Vix Fix Formula
    wvf = ((data["close"].rolling(pd).max() - data["low"])/(data["close"].rolling(pd).max()))*100
    sDev = mult * wvf.rolling(bbl).std()
    midLine = wvf.rolling(bbl).mean()
    lowerBand = midLine - sDev
    upperBand = midLine + sDev
    rangeHigh = wvf.rolling(lb).max() * ph
    
    # Filtered Bar Criteria
    upRange = (data["low"] > data["low"].shift(1)) & (data["close"] > data["high"].shift(1))
    upRange_Aggr = (data["close"] > data["close"].shift(1)) & (data["close"] > data["open"].shift(1))
    
    # Filtered Criteria
    filtered = (wvf.shift(1) >= upperBand.shift(1)) | (wvf.shift(1) >= rangeHigh.shift(1)) & ((wvf < upperBand) & (wvf < rangeHigh))
    filtered_Aggr = ((wvf.shift(1) >= upperBand.shift(1)) | (wvf.shift(1) >= rangeHigh.shift(1))) & ((wvf > upperBand) | (wvf > rangeHigh))
    
    # Alerts Criteria
    alert1 = (wvf >= upperBand) | (wvf >= rangeHigh)
    alert2 = ((wvf.shift(1) >= upperBand.shift(1)) | (wvf.shift(1) >= rangeHigh.shift(1))) & ((wvf < upperBand) & (wvf < rangeHigh))
    alert3 = upRange & (data["close"] > data["close"].shift(_str)) & ((data["close"] < data["close"].shift(ltLB)) | (data["close"] < data["close"].shift(mtLB))) & filtered
    alert4 = upRange_Aggr & (data["close"] > data["close"].shift(_str)) & ((data["close"].shift(_str) < data["close"].shift(ltLB)) | (data["close"] < data["close"].shift(mtLB))) & filtered_Aggr
    
    beware = ((wvf >= upperBand) | (wvf >= rangeHigh))
    vol_buy = (((wvf.shift(1) >= upperBand.shift(1)) | (wvf.shift(1) >= rangeHigh.shift(1))) & ((wvf < upperBand) & (wvf < rangeHigh)))
    pa_buy = alert3
    aggressive = alert4
    
    wvf_blue = "#0CA4DE"
    wvf_gray = "#758494"
    
    data["Matrix_wvf_color"] = np.where((wvf >= upperBand) | (wvf >= rangeHigh), wvf_blue, wvf_gray)
     
    ys1 = ( data["high"] + data["low"] + data["close"] * 2 ) / 4
    rk3 = ys1.ewm(span = nn, adjust = False).mean()
    rk4 = ys1.rolling(nn).std()
    rk5 = (ys1 - rk3 ) * 200 / rk4
    rk6 = rk5.ewm(span = nn, adjust = False).mean()
    up = rk6.ewm(span = nn, adjust = False).mean()
    down = up.ewm(span = nn, adjust = False).mean()
    data["Matrix_Oo"] = np.where((up < down), up, down)
    data["Matrix_Hh"] = data["Matrix_Oo"]
    data["Matrix_Ll"] = np.where((up < down), down, up)
    data["Matrix_Cc"] = data["Matrix_Ll"]
    
    chartSolidGreen = "#3D9970"
    chartSolidRed = "#FF4136"
    
    data["Matrix_vcolor"] = np.select([(data["Matrix_Oo"] > data["Matrix_Cc"]), (up > down)], [chartSolidRed, chartSolidGreen], default = chartSolidRed)

    # -------S/R Zones------
    Lookback = SupResPeriod
    PerCent = SupResPercentage
    Pds = PricePeriod
    
    C3 = CCI(data,Pds )

    Osc = C3
    Value1 = Osc
    Value2 = Value1.rolling(Lookback).max()
    Value3 = Value1.rolling(Lookback).min()
    Value4 = Value2 - Value3
    Value5 = Value4 * ( PerCent / 100 )
    ResistanceLine = Value3 + Value5
    SupportLine = Value2 - Value5
    
    swvfm_precent = swvfm * (ResistanceLine-SupportLine)/(2.2 * rangeHigh)
    
    data["Matrix_wvf_plot"] = wvf * -1 * swvfm_precent
    
    data["Matrix_action_text"] = np.select([beware, vol_buy, pa_buy, aggressive], ["Beware Vola", "Vola Buy", "PA Buy", "Agro Buy"], default = "N/A")
    data["Matrix_action_color"] = np.select([beware, vol_buy, pa_buy, aggressive], [chartSolidRed, chartSolidGreen, chartSolidGreen, "#FF0080"], default = "rgba(0,0,0,0)")
    data["Matrix_action"] = np.select([beware, vol_buy, pa_buy, aggressive], [50.0, 50.0, 50.0, 50.0], default = 0.0)
    
    # Overbought/Oversold/Warning Detail
    highest_up = up.rolling(1).max()
    highest_down = down.rolling(1).max()
    
    data["Matrix_UPshape"] = np.select([((up > ob) & (up>down)), ((up > ob) & (up<down))], [highest_up + 20, highest_down + 20], np.NaN)
    
    lowest_up = up.rolling(1).min()
    lowest_down = down.rolling(1).min()
    
    data["Matrix_DOWNshape"] = np.select([((down < os) & (up>down)), ((down < os) & (up<down))], [lowest_down - 20, lowest_up - 20], np.NaN)
    
    data["Matrix_ob"] = 200.0
    data["Matrix_os"] = -200.0
    
    return data