# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 15:12:15 2021

@author: csandfort
"""
import os as os
from os import walk
from pathlib import Path
import pandas as pd
import numpy as np
import dataRetrieval as dr 
import datetime
import technicals as technicals 
import matplotlib.pyplot as plt
from matplotlib import colors
import constants
import colorMapUtils as cmap_utils

universeInfo = pd.read_csv(os.path.join(os.getcwd(), 'data', "UniverseInfo.csv"), index_col="Ticker")
rosetta_stone = constants.grids

def initialize_asset_df(from_df, is_portfolio = False, ticker_list = None):
    tickers = []
    quantities = []
    entries = []
    lasts = []
    previouses = []
    costBasii = []
    currentValues = []
    ydayValues = []
    weights = []
    pnls = []
    chg1d = []
    chg1w = []
    chg1m = []
    chg3m = []
    chg1d_zs = []
    chg1w_zs = []
    chg1m_zs = []
    chg3m_zs = []
    names = []
    assetClasses = []
    universes = []
    factors = []
    exposures = []
    grids = []
    rvs = []
    rvs1d = []
    rvs1w = []
    rvs1m = []
    trends = []
    trades = []
    momos = []
    bbbs = []
    bbts = []
    bbps = []
    volumeDescs = []
    
    totalCash = 0.0
    
    if ticker_list is None:
        ticker_list = from_df.index.values
    
    if is_portfolio and "SDBA Cash" in from_df.index.values:
        totalCash += from_df.at["SDBA Cash", "Entry"]
    
    if is_portfolio and "Cash" in from_df.index.values:
        totalCash += from_df.at["Cash", "Entry"]
    
        tickers.append("Cash")
        quantities.append(1.0)
        entries.append(totalCash)
        lasts.append(totalCash)
        previouses.append(0.0)
        costBasii.append(totalCash)
        currentValues.append(totalCash)
        ydayValues.append(totalCash)
        weights.append(0.0)
        pnls.append(0.0)
        chg1d.append(0.0)
        chg1w.append(0.0)
        chg1m.append(0.0)
        chg3m.append(0.0)
        chg1d_zs.append(0.0)
        chg1w_zs.append(0.0)
        chg1m_zs.append(0.0)
        chg3m_zs.append(0.0)
        names.append("Cash")
        assetClasses.append("Cash")
        universes.append("Cash")
        factors.append("Cash")
        exposures.append("Cash")
        grids.append("Cash")
        rvs.append(0.0)
        rvs1d.append(0.0)
        rvs1w.append(0.0)
        rvs1m.append(0.0)
        trends.append(0.0)
        trades.append(0.0)
        momos.append(0.0)
        bbbs.append(0.0)
        bbts.append(0.0)
        bbps.append(0.0)
        volumeDescs.append('')
    
    for i in ticker_list:
        if i != "SDBA Cash" and i != "Cash":
            tickers.append(i)
            quantities.append(from_df.at[i, "Quantity"] if is_portfolio else 0.0001)
            entries.append(from_df.at[i, "Entry"] if is_portfolio else 0.0001)
            lasts.append(0.0001)
            previouses.append(0.0001)
            costBasii.append(quantities[-1] * entries[-1])
            currentValues.append(0.0001)
            ydayValues.append(0.0001)
            weights.append(0.0001)
            pnls.append(0.0001)
            chg1d.append(0.0001)
            chg1w.append(0.0001)
            chg1m.append(0.0001)
            chg3m.append(0.0001)
            chg1d_zs.append(0.0001)
            chg1w_zs.append(0.0001)
            chg1m_zs.append(0.0001)
            chg3m_zs.append(0.0001)
            rvs.append(0.0001)
            rvs1d.append(0.0001)
            rvs1w.append(0.0001)
            rvs1m.append(0.0001)
            trends.append(0.0001)
            trades.append(0.0001)
            momos.append(0.0001)
            bbbs.append(0.0001)
            bbts.append(0.0001)
            bbps.append(0.0001)
            volumeDescs.append('')
            
            #Ticker, Name, Asset Class,Universe, Factor, Exposure, GRID
            
            if i in universeInfo.index.values:
                names.append(universeInfo.at[i, "Name"])
                assetClasses.append(universeInfo.at[i, "Asset Class"])
                universes.append(universeInfo.at[i, "Universe"])
                factors.append(universeInfo.at[i, "Factor"])
                exposures.append(universeInfo.at[i, "Exposure"])
                grids.append(universeInfo.at[i, "GRID"])
            else:
                names.append("")
                assetClasses.append("")
                universes.append("")
                factors.append("")
                exposures.append("")
                grids.append("")
    
    data = {
        "id": tickers,
        "Ticker": tickers,
        "Quantity": quantities,
        "Entry": entries,
        "Last": lasts,
        "Previous": previouses,
        "CostBasis": costBasii,
        "CurrentValue": currentValues,
        "YdayValue": ydayValues,
        "Weight": weights,
        "Chg1D": chg1d,
        "Chg1W": chg1w,
        "Chg1M": chg1m,
        "Chg3M": chg3m,
        "Chg1D_zs": chg1d_zs,
        "Chg1W_zs": chg1w_zs,
        "Chg1M_zs": chg1m_zs,
        "Chg3M_zs": chg3m_zs,
        "PnL": pnls,
        "Name": names,
        "Asset Class": assetClasses,
        "Universe": universes,
        "Factor": factors,
        "Exposure": exposures,
        "GRID": grids,
        "RV": rvs,
        "RV1D": rvs1d,
        "RV1W": rvs1w,
        "RV1M": rvs1m,
        "Trend": trends,
        "Trade": trades,
        "Momo": momos,
        "BBBot": bbbs,
        "BBTop": bbts,
        "BBPos": bbps,
        "VolumeDesc": volumeDescs
        }   
     
    df = pd.DataFrame(data, tickers)
    
    return df

def initializeData():
    data = {
        "tabData": initializeTabData(),
        "portfolios": initializePortfolios()
        }
    
    return data

def initializeTabData():
    tab_data_frames = {}
    temp_df = None
    
    for grid in rosetta_stone:
        tab_data_frames[grid] = {}
        for table in rosetta_stone[grid]:
            temp_df = initialize_asset_df(None, False, table["tickers"])
            
            tab_data_frames[grid][table["title"]] = temp_df.to_json(date_format='iso', orient='split')
            
    return tab_data_frames

def initializePortfolios():
    filenames = os.listdir(os.path.join(os.getcwd(), 'portfolios'))  # [] if no file
    
    portfolios = {}
    
    for x in filenames:
        #portfolios[Path(x).stem] = pd.read_csv(os.path.join(os.getcwd(), 'portfolios', x), index_col="Ticker")
        temp = pd.read_csv(os.path.join(os.getcwd(), 'portfolios', x), index_col="Ticker")
        
        portfolio_df = initialize_asset_df(temp, True)
        
        portfolios[Path(x).stem] = {"assets": portfolio_df.to_json(date_format='iso', orient='split'),
                                    "total_value": portfolio_df["CurrentValue"].sum(),
                                    "yday_value": portfolio_df["CurrentValue"].sum()
                                    }
    
    
    combined_positions = pd.DataFrame(columns = ["id", "Ticker", "Quantity", "Entry", "Last", "Previous", "CostBasis",
            "CurrentValue", "YdayValue", "Weight", "Chg1D", "Chg1W", "Chg1M", "Chg3M", "Chg1D_zs", "Chg1W_zs", "Chg1M_zs", "Chg3M_zs",
            "PnL", "Name", "Asset Class" , "Universe", "Factor", "Exposure", "GRID",
            "RV", "RV1D", "RV1W", "RV1M", "Trend", "Trade", "Momo", "BBBot", "BBTop", "BBPos", "VolumeDesc"])
    
    for key in portfolios:
        assets = pd.read_json(portfolios[key]["assets"], orient='split')
        
        for ticker in assets.index.values:
            if ticker in combined_positions.index.values:
                if ticker == "Cash":
                    combined_positions.at[ticker, "Entry"] = combined_positions.at[ticker, "Entry"] + assets.at[ticker, "Entry"]
                    combined_positions.at[ticker, "CostBasis"] = combined_positions.at[ticker, "CostBasis"] + assets.at[ticker, "CostBasis"]
                    combined_positions.at[ticker, "CurrentValue"] = combined_positions.at[ticker, "CurrentValue"] + assets.at[ticker, "CurrentValue"]
                    combined_positions.at[ticker, "YdayValue"] = combined_positions.at[ticker, "YdayValue"] + assets.at[ticker, "YdayValue"]
                    combined_positions.at[ticker, "Last"] += assets.at[ticker, "Last"]
                else:
                    combined_positions.at[ticker, "CostBasis"] = combined_positions.at[ticker, "CostBasis"] + assets.at[ticker, "CostBasis"]
                    combined_positions.at[ticker, "Quantity"] = combined_positions.at[ticker, "Quantity"] + assets.at[ticker, "Quantity"]
                    combined_positions.at[ticker, "Entry"] = combined_positions.at[ticker, "CostBasis"] / combined_positions.at[ticker, "Quantity"]
            else:
                combined_positions.loc[ticker] = [
                    ticker,
                    ticker,
                    assets.at[ticker, "Quantity"],
                    assets.at[ticker, "Entry"],
                    assets.at[ticker, "Last"],
                    assets.at[ticker, "Previous"],
                    assets.at[ticker, "CostBasis"],
                    assets.at[ticker, "CurrentValue"],
                    assets.at[ticker, "YdayValue"],
                    assets.at[ticker, "Weight"],
                    assets.at[ticker, "Chg1D"],
                    assets.at[ticker, "Chg1W"],
                    assets.at[ticker, "Chg1M"],
                    assets.at[ticker, "Chg3M"],
                    assets.at[ticker, "Chg1D_zs"],
                    assets.at[ticker, "Chg1W_zs"],
                    assets.at[ticker, "Chg1M_zs"],
                    assets.at[ticker, "Chg3M_zs"],
                    assets.at[ticker, "PnL"],
                    assets.at[ticker, "Name"],
                    assets.at[ticker, "Asset Class"],
                    assets.at[ticker, "Universe"],
                    assets.at[ticker, "Factor"],
                    assets.at[ticker, "Exposure"],
                    assets.at[ticker, "GRID"],
                    assets.at[ticker, "RV"],
                    assets.at[ticker, "RV1D"],
                    assets.at[ticker, "RV1W"],
                    assets.at[ticker, "RV1M"],
                    assets.at[ticker, "Trend"],
                    assets.at[ticker, "Trade"],
                    assets.at[ticker, "Momo"],
                    assets.at[ticker, "BBBot"],
                    assets.at[ticker, "BBTop"],
                    assets.at[ticker, "BBPos"],
                    assets.at[ticker, "VolumeDesc"]
                    ]
     
    portfolios["Portfolio"] = {"assets": combined_positions.to_json(date_format='iso', orient='split'),
                               "total_value": combined_positions["CurrentValue"].sum(),
                               "yday_value": combined_positions["YdayValue"].sum()
                               }

    return portfolios

# def create_asset_data_table

def update_asset_dfs(data_store):
    startDate = datetime.datetime.strptime('2020-05-01', '%Y-%m-%d')
    endDate = datetime.datetime.today()
    
    temp = None
    allTickers = []
    
    for key in data_store["portfolios"]:
        temp = pd.read_json(data_store["portfolios"][key]['assets'], orient='split')
        allTickers.extend(x for x in temp.index.values if x not in allTickers and x != 'Cash')
    
    for tab in data_store["tabData"]:
        for table_name in data_store["tabData"][tab]:
            temp = pd.read_json(data_store["tabData"][tab][table_name], orient='split')
            allTickers.extend(x for x in temp.index.values if x not in allTickers and x != 'Cash')
    
    dr.GetTdaDataForTickers(allTickers, 'month', 'daily', 1, startDate, endDate, False, True)

def updateAssetTables(data_store):
    # startDate = datetime.datetime.strptime('2020-05-01', '%Y-%m-%d')
    # endDate = datetime.datetime.today()
    
    allTickers = []
    portfolio_table_dfs = {}

    for key in data_store["portfolios"]:
        portfolio_table_dfs[key] = pd.read_json(data_store["portfolios"][key]['assets'], orient='split')
        allTickers.extend(x for x in portfolio_table_dfs[key].index.values if x not in allTickers and x != 'Cash')
    
    tabData_table_dfs = {}
    
    for tab in data_store["tabData"]:
        tabData_table_dfs[tab] = {}
        for table_name in data_store["tabData"][tab]:
            tabData_table_dfs[tab][table_name] = pd.read_json(data_store["tabData"][tab][table_name], orient='split')
            allTickers.extend(x for x in tabData_table_dfs[tab][table_name].index.values if x not in allTickers and x != 'Cash')

    data = dr.GetDataFromCsv(allTickers)
    
    for key in portfolio_table_dfs:
        asset_table = portfolio_table_dfs[key]       
        
        for ticker in asset_table.index.values:
            if ticker != 'Cash':
                asset_table.at[ticker, 'Last'] = data[ticker]['close'][-1]
                asset_table.at[ticker, 'CurrentValue'] = asset_table.at[ticker, 'Last'] * asset_table.at[ticker, 'Quantity']
                asset_table.at[ticker, 'YdayValue'] = data[ticker]['close'][-2] * asset_table.at[ticker, 'Quantity']
                asset_table.at[ticker, 'PnL'] = (data[ticker]['close'][-1] / asset_table.at[ticker, 'Entry']) - 1.0
                
                data, asset_table = apply_technicals_to_asset_df(ticker, data, asset_table)
                
    
        total_value = asset_table["CurrentValue"].sum()
        asset_table["Weight"] = asset_table["CurrentValue"] / total_value
    
        data_store["portfolios"][key] = {"assets": asset_table.to_json(date_format='iso', orient='split'),
                           "total_value": total_value,
                           "yday_value": asset_table["YdayValue"].sum()
                           }
    
    for tab in tabData_table_dfs:
        for table_name in tabData_table_dfs[tab]:
            asset_table = tabData_table_dfs[tab][table_name]
            
            #print(tab, ", ", table_name, ", ", ",".join(asset_table.index.values))
            
            for ticker in asset_table.index.values:
                asset_table.at[ticker, 'Last'] = data[ticker]['close'][-1]
                # asset_table.at[ticker, 'CurrentValue'] = asset_table.at[ticker, 'Last'] * asset_table.at[ticker, 'Quantity']
                # asset_table.at[ticker, 'YdayValue'] = data[ticker]['close'][-2] * asset_table.at[ticker, 'Quantity']
                # asset_table.at[ticker, 'PnL'] = (data[ticker]['close'][-1] / asset_table.at[ticker, 'Entry']) - 1.0
                
                data, asset_table = apply_technicals_to_asset_df(ticker, data, asset_table)
                    
                data_store["tabData"][tab][table_name] = asset_table.to_json(date_format='iso', orient='split')
              
    
    return data_store


def apply_technicals_to_asset_df(ticker, data, asset_df):
    data[ticker] = apply_technicals(data[ticker])
    # data[ticker]['RV1D'] = np.log(data[ticker]['RV'] / data[ticker]['RV'].shift(1))
    # data[ticker]['RV1W'] = np.log(data[ticker]['RV'] / data[ticker]['RV'].shift(5))
    # data[ticker]['RV1M'] = np.log(data[ticker]['RV'] / data[ticker]['RV'].shift(21))
       
    
    asset_df.at[ticker, 'Chg1D'] = data[ticker]['Chg1D'][-1]
    asset_df.at[ticker, 'Chg1W'] = data[ticker]['Chg1W'][-1]
    asset_df.at[ticker, 'Chg1M'] = data[ticker]['Chg1M'][-1]
    asset_df.at[ticker, 'Chg3M'] = data[ticker]['Chg3M'][-1]
    
    asset_df.at[ticker, 'Chg1D_zs'] = data[ticker]['Chg1D_zs'][-1]
    asset_df.at[ticker, 'Chg1W_zs'] = data[ticker]['Chg1W_zs'][-1]
    asset_df.at[ticker, 'Chg1M_zs'] = data[ticker]['Chg1M_zs'][-1]
    asset_df.at[ticker, 'Chg3M_zs'] = data[ticker]['Chg3M_zs'][-1]
    
    asset_df.at[ticker, 'RV'] = data[ticker]['RV'][-1]
    asset_df.at[ticker, 'RV1D'] = data[ticker]['RV'][-2]
    asset_df.at[ticker, 'RV1W'] = data[ticker]['RV'][-6]
    asset_df.at[ticker, 'RV1M'] = data[ticker]['RV'][-22]
    
    asset_df.at[ticker, 'Trend'] = data[ticker]['Trend'][-1]
    asset_df.at[ticker, 'Trade'] = data[ticker]['Trade'][-1]
    asset_df.at[ticker, 'Momo'] = data[ticker]['Momo'][-1]
    asset_df.at[ticker, 'BBBot'] = data[ticker]['BBBot'][-1]
    asset_df.at[ticker, 'BBTop'] = data[ticker]['BBTop'][-1]
    asset_df.at[ticker, 'BBPos'] = data[ticker]['BBPos'][-1]
    asset_df.at[ticker, 'VolumeDesc'] = data[ticker]['VolumeDesc'][-1]
    
    return data, asset_df

def apply_technicals(data):
    data['RV'] = technicals.calcHvZScore(data, 63)
    
    data['Chg1D'] = (data['close'] / data['close'].shift(1)) - 1.0
    data['Chg1W'] = (data['close'] / data['close'].shift(5)) - 1.0
    data['Chg1M'] = (data['close'] / data['close'].shift(21)) - 1.0
    data['Chg3M'] = (data['close'] / data['close'].shift(63)) - 1.0
    
    data.loc[(data['Chg1D'] > 0.0), 'Chg1D_zs'] = technicals.calcZScore(data[data['Chg1D'] > 0.0], 'Chg1D')
    data.loc[(data['Chg1W'] > 0.0), 'Chg1W_zs'] = technicals.calcZScore(data[data['Chg1W'] > 0.0], 'Chg1W')
    data.loc[(data['Chg1M'] > 0.0), 'Chg1M_zs'] = technicals.calcZScore(data[data['Chg1M'] > 0.0], 'Chg1M')
    data.loc[(data['Chg3M'] > 0.0), 'Chg3M_zs'] = technicals.calcZScore(data[data['Chg3M'] > 0.0], 'Chg3M')
    
    
    data.loc[(data['Chg1D'] < 0.0), 'Chg1D_zs'] = technicals.calcZScore(data[data['Chg1D'] < 0.0], 'Chg1D', is_negative = True)
    data.loc[(data['Chg1W'] < 0.0), 'Chg1W_zs'] = technicals.calcZScore(data[data['Chg1W'] < 0.0], 'Chg1W', is_negative = True)
    data.loc[(data['Chg1M'] < 0.0), 'Chg1M_zs'] = technicals.calcZScore(data[data['Chg1M'] < 0.0], 'Chg1M', is_negative = True)
    data.loc[(data['Chg3M'] < 0.0), 'Chg3M_zs'] = technicals.calcZScore(data[data['Chg3M'] < 0.0], 'Chg3M', is_negative = True)
    
    trend, outlook = technicals.getTrend(data, 'low', 'high', 'close', 63)
    data['Trend'] = trend
    
    trade, trade_outlook = technicals.getTrend(data, 'low', 'high', 'close', 21)
    data['Trade'] = trade
    
    data['Momo'] = (data['close'] > data['close'].shift(21)).astype(np.float64)
    
    BridgeBandBottom, BridgeBandTop = technicals.BridgeBands(data, data.close, 15)
    data['BBBot'] = BridgeBandBottom
    data['BBTop'] = BridgeBandTop
    
    data['BBPos'] = (BridgeBandTop - data['close']) / (BridgeBandTop - BridgeBandBottom)
    data.loc[(data['BBPos'] > 1.), 'BBPos'] = 1.0
    data.loc[(data['BBPos'] < 0.), 'BBPos'] = 0.0
    
    data = technicals.calcVolumeMetrics(data)
    
    data.loc[(data['VolumeEnum'] == 0.0) & (data['close'] > data['close'].shift(1)), 'VolumeDesc'] = 'Weak'
    data.loc[(data['VolumeEnum'] == 1.0) & (data['close'] > data['close'].shift(1)), 'VolumeDesc'] = 'Moderate'
    data.loc[(data['VolumeEnum'] == 2.0) & (data['close'] > data['close'].shift(1)), 'VolumeDesc'] = 'Strong'
    data.loc[(data['VolumeEnum'] == 3.0) & (data['close'] > data['close'].shift(1)), 'VolumeDesc'] = 'Absolute'
    
    data.loc[(data['VolumeEnum'] == -0.0) & (data['close'] < data['close'].shift(1)), 'VolumeDesc'] = 'Weak'
    data.loc[(data['VolumeEnum'] == -1.0) & (data['close'] < data['close'].shift(1)), 'VolumeDesc'] = 'Moderate'
    data.loc[(data['VolumeEnum'] == -2.0) & (data['close'] < data['close'].shift(1)), 'VolumeDesc'] = 'Strong'
    data.loc[(data['VolumeEnum'] == -3.0) & (data['close'] < data['close'].shift(1)), 'VolumeDesc'] = 'Absolute'
    
    return data

def get_data_for_ticker(ticker, displayLookback = None):
    startDate = datetime.datetime.strptime('2020-05-01', '%Y-%m-%d')
    endDate = datetime.datetime.today()
    data = dr.GetTdaData(ticker, 'month', 'daily', 1, startDate, endDate, False, True)
    data = apply_technicals(data)
    
    if displayLookback is not None:
        data = data[datetime.date.today() - datetime.timedelta(days=displayLookback):]
    
    return data

def get_single_cmap_value(s, m, M, cmap='seismic', reverse = False, low=0, high=0):
    rng = M - m
    norm = colors.Normalize(m - (rng * low),
                            M + (rng * high))
    normed = norm(s)
    
    the_cmap = plt.cm.get_cmap(cmap).reversed() if reverse else plt.cm.get_cmap(cmap)
    
    c = [colors.rgb2hex(x) for x in the_cmap(normed)]
    
    # print("test")
    # print(s[0], "    ", normed[0], "   ", c[0])
    
    return c

def get_up_volume_color(v):
    
    c = "#000000"
    
    if v == 0.0: c = "#99c2af"
    elif v == 1.0: c = "#66a487"
    elif v == 2.0: c = "#32865e"
    elif v == 3.0: c = "#006837"
    
    return c

def get_cmap_value(s, m, M, cmap='seismic', reverse = False, low=0, high=0):
    rng = M - m
    norm = colors.Normalize(m - (rng * low),
                            M + (rng * high))
    normed = norm(s.values)
    
    the_cmap = cmap_utils.get_cmap(cmap).reversed() if reverse else cmap_utils.get_cmap(cmap)
    
    c = [colors.rgb2hex(x) for x in the_cmap(normed)]
    return c

def get_single_cmap_style(val, m, M, cmap='seismic', reverse = False, low=0, high=0, st_threshold_1 = 1.0, st_threshold_2 = -1.0,
                           white_threshold_1 = 1.0, white_threshold_2 = -1.0, data_col = None, inverse_text_color_rule = False):
    styles = {}

    color = get_single_cmap_value([val], m, M, cmap, reverse, low, high)[0]
    
    styles = {
        "backgroundColor": color
        }
    
    if inverse_text_color_rule:
        if (val <= st_threshold_1 and val >= st_threshold_2):
            styles["color"] = "white"
        elif (val > white_threshold_1 or val < white_threshold_2):
            styles["color"] = "#272727"
    else:
        if (val <= st_threshold_1 and val >= st_threshold_2):
            styles["color"] = "#272727"
        elif (val > white_threshold_1 or val < white_threshold_2):
            styles["color"] = "white"
      
    return styles

def get_column_cmap_values(df, col, m, M, cmap='seismic', reverse = False, low=0, high=0, st_threshold_1 = 1.0, st_threshold_2 = -1.0,
                           white_threshold_1 = 1.0, white_threshold_2 = -1.0, data_col = None, inverse_text_color_rule = False):
    styles = []
    
    if data_col is None:
        data_col = col
    
    color_list = get_cmap_value(df[data_col], m, M, cmap, reverse, low, high)
    
    #print(col, ", ", data_col, ", ", len(color_list), ", ", (color_list[0] if len(color_list) > 0 else "None"))
    
    i = 0
    for idx in df.index.values:
        if idx != 'Cash':
            styles.append({
                'if': {
                    'filter_query': '{{{col}}} = {val} and {{{col}}} != 0.0001'.format(col = data_col, val = df.at[idx, data_col]),
                    'column_id': col
                    },
                    'backgroundColor': color_list[i]
                })
        
        i += 1
    
    if inverse_text_color_rule:
        styles.append({
            'if': {
                'filter_query': '{{{col}}} <= {st_threshold_1} and {{{col}}} >= {st_threshold_2}'.format(col = data_col, st_threshold_1 = st_threshold_1, st_threshold_2 = st_threshold_2),
                'column_id': [col]
            },
            'color': 'white'
        })
    
        styles.append({
            'if': {
                'filter_query': '{{{col}}} > {white_threshold_1} or {{{col}}} < {white_threshold_2}'.format(col = data_col, white_threshold_1 = white_threshold_1, white_threshold_2 = white_threshold_2),
                'column_id': [col]
            },
            'color': '#272727'
        })
    else:
        styles.append({
            'if': {
                'filter_query': '{{{col}}} <= {st_threshold_1} and {{{col}}} >= {st_threshold_2}'.format(col = data_col, st_threshold_1 = st_threshold_1, st_threshold_2 = st_threshold_2),
                'column_id': [col]
            },
            'color': '#272727'
        })
    
        styles.append({
            'if': {
                'filter_query': '{{{col}}} > {white_threshold_1} or {{{col}}} < {white_threshold_2}'.format(col = data_col, white_threshold_1 = white_threshold_1, white_threshold_2 = white_threshold_2),
                'column_id': [col]
            },
            'color': 'white'
        })
      
    return styles

def getVolumeStyle(asset):
    styles = {}


    if asset.VolumeDesc == "Weak" and asset.Chg1D < 0.0:
        styles = {'backgroundColor': "#FCBCA2",
        'color': '#272727'}
    elif asset.VolumeDesc == "Moderate" and asset.Chg1D < 0.0:
        styles = {'backgroundColor': "#FB6B4B",
        'color': '#272727'}
    elif asset.VolumeDesc == "Strong" and asset.Chg1D < 0.0:
        styles = {'backgroundColor': "#CB181D",
        'color': 'white'}
    elif asset.VolumeDesc == "Absolute" and asset.Chg1D < 0.0:
        styles = {'backgroundColor': "#67000D",
        'color': 'white'}
    elif asset.VolumeDesc == "Weak" and asset.Chg1D > 0.0: 
        styles = {'backgroundColor': "#C7E9C0",
        'color': '#272727'}
    elif asset.VolumeDesc == "Moderate" and asset.Chg1D > 0.0:
        styles = {'backgroundColor': "#73C476",
        'color': '#272727'}
    elif asset.VolumeDesc == "Strong" and asset.Chg1D > 0.0:
        styles = {'backgroundColor': "#228A44",
        'color': 'white'}
    elif asset.VolumeDesc == "Absolute" and asset.Chg1D > 0.0:
        styles = {'backgroundColor': "#00441B",
        'color': 'white'}


    return styles   
      
    
#t = initializePortfolios()
#t = updatePortfolios(t)