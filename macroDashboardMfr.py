# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 16:57:19 2022

@author: csandfort
"""
import dash
from dash import dash_table, ALL
from dash_table import DataTable
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Input, Output, State
import portfolioUtilities as portUtils
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import assetClassesMfr as ac
from scipy.stats import pearsonr
import numpy as np
import argparse
import helper
import performance as perf
import plotly.express as px
from itertools import cycle
import eurodollarCurveHelper as edch

parser = argparse.ArgumentParser()

parser.add_argument("-r", "--refresh", help="refresh data",
                    action="store_true")

parser.add_argument("-d", "--debug", help="debug",
                    action="store_true")

parser.add_argument("-g", "--generic_ranges", help="generic ranges",
                    action="store_true")

args = parser.parse_args()

print(args.generic_ranges)

if args.refresh:
    helper.refreshData()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

data_table_style_header_dict = {
    "backgroundColor": "#15191e",
    "color": "#e1e5ea",
    "fontWeight": "bold"
}

data_table_style_cell_dict = {
    "backgroundColor": "#272727",
    "color": "#c4cad4",
    'border': '1px solid #737373',
    "padding-left": 8,
    "padding-right": 8,
    "padding-top": 6,
    "padding-bottom": 6,
    "fontSize": "1rem"
}

tdLabelStyles = {"fontWeight": "bold",
               "backgroundColor": "rgb(45, 45, 45)"}

greenColor = "#77b300"
redColor = 'IndianRed'

chartSolidGreen = "#3D9970"
chartTransGreen = 'rgba(61,153,112,0.2)'
chartSolidRed = "#FF4136"
chartTransRed = 'rgba(255,65,54,0.2)'
chartSolidNeutral = "#ffff1c"
chartTransNeutral = 'rgba(255,255,28,0.2)'
chartSolidNeutralDanger = "#0085FF"
chartTransNeutralDanger = 'rgba(49,77,102,0.2)'

amc = ac.getAllRangeChanges(args.generic_ranges)

eurodollarCurveDf = edch.constructCurve(args.refresh)

def extendAllAssets(collection):
    for ticker in collection:
        if ticker not in allAssets:
            allAssets[ticker] = collection[ticker]

print("portfolio")
portfolio = ac.AssetCollection("Portfolio.csv", args.generic_ranges, generic_ranges = args.generic_ranges)
print("marketSnapshot")
marketSnapshot = ac.AssetCollection("MarketSnapshot.csv", args.generic_ranges, generic_ranges = args.generic_ranges)
print("potentials")
potentials = ac.AssetCollection("Potentials.csv", args.generic_ranges, generic_ranges = args.generic_ranges)
print("benchmarks")
benchmarks = ac.AssetCollection("Benchmarks.txt", args.generic_ranges, generic_ranges = args.generic_ranges)

allAssets = {}

extendAllAssets(portfolio.collection)
extendAllAssets(marketSnapshot.collection)
extendAllAssets(potentials.collection)
extendAllAssets(benchmarks.collection)

watchlistDict = {}
watchlistDict["Cash"] = ac.Asset("Cash", 1, 1000000000.0)

for ticker in allAssets:
    if ticker not in portfolio.collection and ticker not in watchlistDict:
        watchlistDict[ticker] = allAssets[ticker]


print("watchlist")
watchlist = ac.AssetCollection(None, watchlistDict, isPortfolio = False, generic_ranges = args.generic_ranges)

print("peformance")
performanceDict = perf.getPortfolioAndBenchmarksPerformanceDict()

print("done")

equityTickers = ["SPY", "QQQ", "IWM", "VIX", "UVXY"]
bondTickers = ["MOVE", "US10Y", "US30Y", "TLT", "HYG", "LQD"]

def get_assets_data_table(name, assetCollection):
    columns = [
        dict(id='Ticker', name='Ticker'),
        # dict(id='Quantity', name='Quantity', type='numeric',
        #     format={"specifier": ".0f"}),
        # dict(id='Entry', name='Entry', type='numeric',
        #      format={"specifier": "$.2f"}),
         # dict(id='Last', name='Last', type='numeric',
         #      format={"specifier": "$.2f"})
        ]
    
    # columns.extend([dict(id='Last', name='Last', type='numeric',
    #      format={"specifier": "$.2f"}),

    columns.extend([
    dict(id='Weight', name='Weight', type='numeric',
         format={"specifier": ".2%"}),
    # dict(id='VaR', name='VaR', type='numeric',
    #      format={"specifier": ".2%"}),
    dict(id='PnL', name='PnL', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='PortPnL', name='Port PnL', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='LR', name='LR', type='numeric',
         format={"specifier": "$.2f"}),
    # dict(id='Stop', name='Stop', type='numeric',
    #      format={"specifier": "$.2f"}),
    dict(id='Last', name='Last', type='numeric',
         format={"specifier": "$.2f"}),
    # dict(id='Target', name='Target', type='numeric',
    #      format={"specifier": "$.2f"}),
    dict(id='TR', name='TR', type='numeric',
         format={"specifier": "$.2f"}),
    dict(id='RPos', name='R Pos', type='numeric',
         format={"specifier": ".2f"}),
    dict(id='TrendEmoji', name='Trend'),
    dict(id='MomentumEmoji', name='Momentum'),
    dict(id='VolumeDesc', name='Volume'),
    dict(id='Chg1D', name='1D', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='Chg1M', name='1M', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='Chg3M', name='3M', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='Crowding_Text', name='Crowding', type='numeric'),
    dict(id='Stop_Ratio', name='Stop_Ratio', type='numeric',
         format={"specifier": ".2f"}),
    ])


    styles = []

    styles.extend(
        [{
            'if': {'column_id': 'TrendEmoji'},
            'textAlign': 'center'
        },
        {
            'if': {'column_id': 'MomentumEmoji'},
            'textAlign': 'center'
        },
        {
            'if': {
                'filter_query': '{PnL} > 0',
                'column_id': 'PnL'
            },
            'color': greenColor
        },
        {
            'if': {
                'filter_query': '{PnL} < 0',
                'column_id': 'PnL'
            },
            'color': redColor
        },
        {
            'if': {
                'filter_query': '{PortPnL} > 0',
                'column_id': 'PortPnL'
            },
            'color': greenColor
        },
        {
            'if': {
                'filter_query': '{PortPnL} < 0',
                'column_id': 'PortPnL'
            },
            'color': redColor
        },
        {
            'if': {
                'filter_query': '{Chg1D} > 0',
                'column_id': 'Chg1D'
            },
            'color': greenColor
        },
        {
            'if': {
                'filter_query': '{Chg1D} < 0',
                'column_id': 'Chg1D'
            },
            'color': redColor
        },
        {
            'if': {
                'filter_query': '{Chg1M} > 0',
                'column_id': 'Chg1M'
            },
            'color': greenColor
        },
        {
            'if': {
                'filter_query': '{Chg1M} < 0',
                'column_id': 'Chg1M'
            },
            'color': redColor
        },
        {
            'if': {
                'filter_query': '{Chg3M} > 0',
                'column_id': 'Chg3M'
            },
            'color': greenColor
        },
        {
            'if': {
                'filter_query': '{Chg3M} < 0',
                'column_id': 'Chg3M'
            },
            'color': redColor
        },
        {
            'if': {
                'filter_query': '{VolumeDesc} = "Weak" and {Chg1D} < 0.0',
                'column_id': 'VolumeDesc'
            },
            'backgroundColor': "#FCBCA2",
            'color': '#272727'
        },
        {
            'if': {
                'filter_query': '{VolumeDesc} = "Moderate" and {Chg1D} < 0.0',
                'column_id': 'VolumeDesc'
            },
            'backgroundColor': "#FB6B4B",
            'color': '#272727'
        },
        {
            'if': {
                'filter_query': '{VolumeDesc} = "Strong" and {Chg1D} < 0.0',
                'column_id': 'VolumeDesc'
            },
            'backgroundColor': "#CB181D",
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{VolumeDesc} = "Absolute" and {Chg1D} < 0.0',
                'column_id': 'VolumeDesc'
            },
            'backgroundColor': "#67000D",
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{VolumeDesc} = "Weak" and {Chg1D} > 0.0',
                'column_id': 'VolumeDesc'
            },
            'backgroundColor': "#C7E9C0",
            'color': '#272727'
        },
        {
            'if': {
                'filter_query': '{VolumeDesc} = "Moderate" and {Chg1D} > 0.0',
                'column_id': 'VolumeDesc'
            },
            'backgroundColor': "#73C476",
            'color': '#272727'
        },
        {
            'if': {
                'filter_query': '{VolumeDesc} = "Strong" and {Chg1D} > 0.0',
                'column_id': 'VolumeDesc'
            },
            'backgroundColor': "#228A44",
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{VolumeDesc} = "Absolute" and {Chg1D} > 0.0',
                'column_id': 'VolumeDesc'
            },
            'backgroundColor': "#00441B",
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{Crowding_Text} = "Squeeze"',
                'column_id': 'Crowding_Text'
            },
            'backgroundColor': "#00441B",
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{Crowding_Text} = "Trim Longs"',
                'column_id': 'Crowding_Text'
            },
            'backgroundColor': "#FCBCA2",
            'color': '#272727'
        },
        {
            'if': {
                'filter_query': '{Crowding_Text} = "Get Long"',
                'column_id': 'Crowding_Text'
            },
            'backgroundColor': "#228A44",
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{Crowding_Text} = "Puke"',
                'column_id': 'Crowding_Text'
            },
            'backgroundColor': "#67000D",
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{Crowding_Text} = "Trim Shorts"',
                'column_id': 'Crowding_Text'
            },
            'backgroundColor': "#C7E9C0",
            'color': '#272727'
        },
        {
            'if': {
                'filter_query': '{Crowding_Text} = "Get Short"',
                'column_id': 'Crowding_Text'
            },
            'backgroundColor': "#CB181D",
            'color': 'white'
        }])
    
    styles.extend(portUtils.get_column_cmap_values(assetCollection.df, 'RPos', 0.0, 1.0, cmap='RdYlGn', reverse=False, low=0, high=0,
                                                   st_threshold_1=0.75, st_threshold_2=0.25, white_threshold_1=0.75, white_threshold_2=0.25))
    # for t in assetCollection.collection:
    #     asset = assetCollection.collection[t]
    #     if (asset.Stop > 0.0):
    #         stopBgColor = portUtils.get_single_cmap_value([asset.Stop_Ratio], 0.0, 1.0, cmap='Stops')[0]

    #         styles.append({
    #             'if': {
    #                 'filter_query': f'{{Ticker}} = "{asset.ticker}"',
    #                 'column_id': 'Stop'
    #             },
    #             'backgroundColor': stopBgColor,
    #             'color': '#c4cad4'
    #         })
            
    #     if (asset.Target > 0.0):
    #         targetBgColor = portUtils.get_single_cmap_value([asset.Target_Ratio], 0.0, 1.0, cmap='Targets')[0]

    #         styles.append({
    #             'if': {
    #                 'filter_query': f'{{Ticker}} = "{asset.ticker}"',
    #                 'column_id': 'Target'
    #             },
    #             'backgroundColor': targetBgColor,
    #             'color': '#c4cad4'
    #         })
            
    # styles.append({
    #     'if': {
    #         'filter_query': '{Stop} > {Last}',
    #         'column_id': 'Stop'
    #     },
    #     'fontWeight': "bolder",
    #     'color': '#272727'
    # })
    
    # styles.append({
    #     'if': {
    #         'filter_query': '{Target} < {Last}',
    #         'column_id': 'Target'
    #     },
    #     'fontWeight': "bolder",
    #     'color': '#272727'
    # })

    styles.append({
        'if': {
            'filter_query': '{Ticker} = "Cash"',
            'column_id': ["PnL", "Chg1D", "Chg1M", "Chg3M", "TrendEmoji", "MomentumEmoji", "RPos", "VolumeDesc", "LR", "TR", "Last",
                           "Crowding_Score", "Crowding_Text", "Stop", "Target", "VaR", "PortPnL",
                          ]
        },
        'color': 'transparent',
        'backgroundColor': 'rgb(39, 39, 39)'
    })
    
    styles.append({
        'if': {
            'filter_query': '{Ticker} = "Footer"',
            'column_id': ["Ticker", "PnL", "Chg1D", "Chg1M", "Chg3M", "TrendEmoji", "MomentumEmoji", "RPos", "VolumeDesc", "LR", "TR", "Last",
                           "Crowding_Score", "Crowding_Text", "Stop", "Target", "Weight",
                          ]
        },
        'color': 'transparent',
        'backgroundColor': 'rgb(39, 39, 39)'
    })

    assetsDataTable = DataTable(
        id="{}_assets_data_table".format(name.replace(" ", "_")),
        data=assetCollection.df.to_dict("records"),
        columns=columns,
        hidden_columns=['Stop_Ratio'],
        css=[{"selector": ".dash-spreadsheet-menu", "rule": "display: none"}],
        sort_action='native',
        style_header=data_table_style_header_dict,
        style_cell=data_table_style_cell_dict,
        style_data_conditional=styles
    )

    return assetsDataTable

def get_side_bar():
    header_row = html.Tr([html.Th("Sym"),
                         html.Th("Last"),
                         html.Th("Chg"),
                         html.Th("Trd"),
                         html.Th("Mtum"),
                         html.Th("R Pos"),
                         html.Th("Crowding")],
                        className = "font-weight-bold",
                        style = {"backgroundColor": "#15191E",
                                 "fontSize": "1.1em"})
    
    table_header = [
        html.Thead(html.Tr([html.Th("Equities", colSpan = 7, className="bg-info font-weight-bolder text-center h5")]))
    ]
    
    rows = []
    rows.append(header_row)    
    
    index = 0
    
    for ticker in equityTickers:
        asset = marketSnapshot.collection[ticker]
        rows.append(html.Tr([html.Td(ticker, className = "font-weight-bold", id = {
            "type": "ticker-td",
            "index": f"{index}:equities"
            }),
                             html.Td(f"${asset.last:.2f}"),
                             html.Td(f"{asset.Chg1D:.2%}",
                                 style = {"color": greenColor if asset.Chg1D > 0.0 else redColor}),
                             html.Td(asset.TrendEmoji, className = "text-center"),
                             html.Td(asset.MomentumEmoji, className = "text-center"),
                             html.Td(f"{asset.RPos:.2f}", style = portUtils.get_single_cmap_style(asset.RPos, 0.0, 1.0, cmap='RdYlGn', reverse=False, low=0, high=0,
                                                                                                  st_threshold_1=0.75, st_threshold_2=0.25, white_threshold_1=0.75, white_threshold_2=0.25)),
                             html.Td(asset.Crowding_Text, style={'color': asset.Crowding_TextColor, 'backgroundColor': asset.Crowding_Color})],
                            style = {"backgroundColor": "#272727"}))
        
        index += 1
    
    table_body = [html.Tbody(rows)]
    
    equities_table = dbc.Table(table_header + table_body, bordered=False, id="market_snapshot_equities_table", className="white_table compact_table")
    
    #### Bonds/Credit
    table_header = [
        html.Thead(html.Tr([html.Th("Bonds/Credit", colSpan = 7, className="bg-warning font-weight-bolder text-center h5")]))
    ]
    
    rows = []
    rows.append(header_row)    
    
    for ticker in bondTickers:
        asset = marketSnapshot.collection[ticker]
        
        isPercent = False
        
        if ticker in ac.tickerLookup:
            if "isPercent" in ac.tickerLookup[ticker]:
                isPercent = True
        
        rows.append(html.Tr([html.Td(ticker, className = "font-weight-bold", id = {
            "type": "ticker-td",
            "index": f"{index}:bonds"
            }),
                             html.Td(f"{asset.last/100.0:.2%}" if isPercent else f"${asset.last:.2f}"),
                             html.Td(f"{asset.Chg1D:.2%}",
                                 style = {"color": greenColor if asset.Chg1D > 0.0 else redColor}),
                             html.Td(asset.TrendEmoji, className = "text-center"),
                             html.Td(asset.MomentumEmoji, className = "text-center"),
                             html.Td(f"{asset.RPos:.2f}", style = portUtils.get_single_cmap_style(asset.RPos, 0.0, 1.0, cmap='RdYlGn', reverse=False, low=0, high=0,
                                                                                                  st_threshold_1=0.75, st_threshold_2=0.25, white_threshold_1=0.75, white_threshold_2=0.25)),
                             html.Td(asset.Crowding_Text, style={'color': asset.Crowding_TextColor, 'backgroundColor': asset.Crowding_Color})],
                            style = {"backgroundColor": "#272727"}))
        
        index += 1
    
    table_body = [html.Tbody(rows)]
    
    bonds_table = dbc.Table(table_header + table_body, bordered=False, id="bonds_and_credit_table", className="white_table compact_table")
    
    #### Potentials
    table_header = [
        html.Thead(html.Tr([html.Th("Potentials", colSpan = 7, className="bg-primary font-weight-bolder text-center h5")]))
    ]
    
    rows = []
    rows.append(header_row)    
    
    for ticker in potentials.collection:
        if ticker == "Cash":
            continue
        
        asset = potentials.collection[ticker]
        
        isPercent = False
        
        if ticker in ac.tickerLookup:
            if "isPercent" in ac.tickerLookup[ticker]:
                isPercent = True
        
        rows.append(html.Tr([html.Td(ticker, className = "font-weight-bold", id = {
            "type": "ticker-td",
            "index": f"{index}:potentials"
            }),
                             html.Td(f"{asset.last/100.0:.2%}" if isPercent else f"${asset.last:.2f}"),
                             html.Td(f"{asset.Chg1D:.2%}",
                                 style = {"color": greenColor if asset.Chg1D > 0.0 else redColor}),
                             html.Td(asset.TrendEmoji, className = "text-center"),
                             html.Td(asset.MomentumEmoji, className = "text-center"),
                             html.Td(f"{asset.RPos:.2f}", style = portUtils.get_single_cmap_style(asset.RPos, 0.0, 1.0, cmap='RdYlGn', reverse=False, low=0, high=0,
                                                                                                  st_threshold_1=0.75, st_threshold_2=0.25, white_threshold_1=0.75, white_threshold_2=0.25)),
                             html.Td(asset.Crowding_Text, style={'color': asset.Crowding_TextColor, 'backgroundColor': asset.Crowding_Color})],
                            style = {"backgroundColor": "#272727"}))
        
        index += 1
    
    table_body = [html.Tbody(rows)]
    
    potentials_table = dbc.Table(table_header + table_body, bordered=False, id="potentials_table", className="white_table compact_table")
    
    recentChangesCard = dbc.Card(
        [dbc.CardHeader(html.H5("Recent Changes", className="mb-0", style=dict(fontWeight = 700)),
                        className="bg-secondary text-white text-center", style=dict(paddingTop = ".35rem", paddingBottom = ".35rem")),
    dbc.CardBody(
        dbc.ListGroup(
            [x.getListGroupItem(smallFont = True, showTicker = True) for x in amc[:50]],
            flush=True,
            style=dict(height = "400px", overflow = "auto")
            ),
        className = "p-0"
        )]
    )
    
    return [equities_table, bonds_table, potentials_table, recentChangesCard]

def getAssetsDataTableWrapper(table_name, assets, header_class):
    table_header = [
        html.Thead(html.Tr([html.Th(table_name.capitalize(), className=f"{header_class} font-weight-bolder text-center h5")]))
    ]
    
    rows = [] 
    rows.append(html.Tr([html.Td(get_assets_data_table(table_name, assets), className = "p-0")]))
    
    table_body = [html.Tbody(rows)]
    
    table = dbc.Table(table_header + table_body, bordered=False, striped=False, hover=False)
    
    return table

def getFillColor(outlook):
    color = 'blue'
    if outlook == 1:
        color = chartTransGreen
    elif outlook == 0:
        color = chartTransNeutral
    elif outlook == -1:
        color = chartTransRed
        
    return color

def getSolidColor(outlook):
    color = 'blue'
    if outlook == 1:
        color = chartSolidGreen
    elif outlook == 0:
        color = chartSolidNeutral
    elif outlook == -1:
        color = chartSolidRed
        
    return color

def addUpVolume(fig, df, name, enumValue, row, col):
    volume = df.loc[(df["IsUp"] == True) & (df["VolumeEnum"] == enumValue)]
    
    volume_colors = portUtils.get_cmap_value(volume["VolumeEnum"], -1, 3, 'Greens', False)
    
    fig.add_trace(go.Bar(x=volume.index.values, y=volume["volume"],
                showlegend=True,
                name=name,
                legendgroup="Volume",
                width = 86400000,
                marker_color = volume_colors),
                row=row, col=col)
    
def addDownVolume(fig, df, name, enumValue, row, col):
    volume = df.loc[(df["IsUp"] == False) & (df["VolumeEnum"] == enumValue)]
    
    volume_colors = portUtils.get_cmap_value(volume["VolumeEnum"], -3, 1, 'Reds', True)
    
    fig.add_trace(go.Bar(x=volume.index.values, y=volume["volume"],
                showlegend=True,
                name=name,
                legendgroup="Volume",
                width = 86400000,
                marker_color= volume_colors),
                  row=row, col=col)
    
def addCrowding(fig, df, name, row, col):
    crowding = df.loc[(df["crowding_text"] == name)]
    
    crowding_colors = {
        "Squeeze": "#00441B",
        "Trim Longs": "#FCBCA2",
        "Trim Shorts": "#C7E9C0",
        "Puke": "#67000D",
        "Get Long": "#228A44",
        "Get Short": "#CB181D",
        }

    fig.add_trace(go.Bar(x=crowding.index.values, y=crowding["crowding_score"],
                showlegend=True,
                name=name,
                legendgroup="Crowding",
                legendgrouptitle_text="Crowding",
                width = 86400000,
                marker_color= crowding_colors[name]),
                  row=row, col=col)

def drawCandlestickChart(fig, df, isPercent, row, col, showLegend = True):
    fig.update_yaxes({
            "title": {"text": "Price", "standoff": 25},
            "tickformat": ".2f",
            "side": "right",
            "tickprefix": "      " if isPercent else "     $",
            "ticksuffix": "%" if isPercent else ""
        }, row=row, col=col)
    
    #%% BridgeBands/Trend
    idxs = df.index.values
    startIndex = df.index.values[0]
    lenIdxs = len(idxs)

    for i in range(1, lenIdxs - 1):
        # Switch from NA to trend
        if pd.isna(df.at[df.index.values[i - 1], "TrendInt"]) and not pd.isna(df.at[df.index.values[i], "TrendInt"]):
            startIndex = df.index.values[i]
            df.at[df.index.values[i-1], "TR"] = df.at[df.index.values[i], "TR"]
            df.at[df.index.values[i-1], "LR"] = df.at[df.index.values[i], "LR"]
        # Switch in trend
        # or switch from trend to NA
        elif ((not pd.isna(df.at[df.index.values[i - 1], "TrendInt"]) and not pd.isna(df.at[df.index.values[i], "TrendInt"])
            and df.at[df.index.values[i - 1], "TrendInt"] != df.at[df.index.values[i], "TrendInt"])
              
              or (not pd.isna(df.at[df.index.values[i - 1], "TrendInt"]) and pd.isna(df.at[df.index.values[i], "TrendInt"]))
              ):
            
            
            chunk_df = df[startIndex:df.index.values[i]]

            fig.add_trace(go.Scatter(x=chunk_df.index.values, y=chunk_df["TR"],
                                      showlegend=False,
                                      mode='lines',
                                      line=dict(
                color=getSolidColor(df.at[df.index.values[i - 1], "TrendInt"]),
                width=1,
                dash='dot')), row=row, col=col)

            fig.add_trace(go.Scatter(x=chunk_df.index.values, y=chunk_df["LR"],
                            showlegend=False,
                            mode='lines',
                            line=dict(
                            color=getSolidColor(df.at[df.index.values[i - 1], "TrendInt"]),
                            width=1,
                            dash='dot'),
                            fill='tonexty',
                            fillcolor=getFillColor(df.at[df.index.values[i - 1], "TrendInt"])), row=row, col=col)
            
            startIndex = df.index.values[i]

    drawLastChunk = False 
    lastChunkLineColor = None
    lastChunkFillColor = None
    
    drawPreviousChunk = False
    previousChunkStartIndex = None
    previousChunkLineColor = None
    previousChunkFillColor = None

    if(pd.isna(df.at[df.index.values[-2], "TrendInt"]) and not pd.isna(df.at[df.index.values[-1], "TrendInt"])):
        drawLastChunk = True
        startIndex = df.index.values[-2]
        df.at[df.index.values[-2], "TR"] = df.at[df.index.values[-1], "TR"]
        df.at[df.index.values[-2], "LR"] = df.at[df.index.values[-1], "LR"]
        lastChunkLineColor = getSolidColor(df.at[df.index.values[-1], "TrendInt"])
        lastChunkFillColor = getFillColor(df.at[df.index.values[-1], "TrendInt"])
    elif(not pd.isna(df.at[df.index.values[-2], "TrendInt"]) and not pd.isna(df.at[df.index.values[-1], "TrendInt"])
       and df.at[df.index.values[-2], "TrendInt"] != df.at[df.index.values[-1], "TrendInt"]):
        if(not pd.isna(df.at[df.index.values[-3], "TrendInt"])):
            drawPreviousChunk = True
            previousChunkStartIndex = startIndex
            previousChunkLineColor = getSolidColor(df.at[df.index.values[-3], "TrendInt"])
            previousChunkFillColor = getFillColor(df.at[df.index.values[-3], "TrendInt"])
            
        drawLastChunk = True
        startIndex = df.index.values[-2]
        lastChunkLineColor = getSolidColor(df.at[df.index.values[-1], "TrendInt"])
        lastChunkFillColor = getFillColor(df.at[df.index.values[-1], "TrendInt"])
    elif(not pd.isna(df.at[df.index.values[-2], "TrendInt"]) and not pd.isna(df.at[df.index.values[-1], "TrendInt"])
        and df.at[df.index.values[-2], "TrendInt"] == df.at[df.index.values[-1], "TrendInt"]):
         drawLastChunk = True
         lastChunkLineColor = getSolidColor(df.at[df.index.values[-1], "TrendInt"])
         lastChunkFillColor = getFillColor(df.at[df.index.values[-1], "TrendInt"])
    

    if (drawPreviousChunk):
        chunk_df = df[previousChunkStartIndex:df.index.values[-2]]
            
        
        fig.add_trace(go.Scatter(x=chunk_df.index.values, y=chunk_df["TR"],
                                  showlegend=False,
                                  mode='lines',
                                  line=dict(
            color=previousChunkLineColor,
            width=1,
            dash='dot')), row=row, col=col)
    
        fig.add_trace(go.Scatter(x=chunk_df.index.values, y=chunk_df["LR"],
                          showlegend=False,
                          mode='lines',
                          line=dict(
                        color=previousChunkLineColor,
                        width=1,
                        dash='dot'),
                        fill='tonexty',
                        fillcolor=previousChunkFillColor), row=row, col=col)

    if (drawLastChunk):
        chunk_df = df[startIndex:df.index.values[-1]]
            
        
        fig.add_trace(go.Scatter(x=chunk_df.index.values, y=chunk_df["TR"],
                                  showlegend=False,
                                  mode='lines',
                                  line=dict(
            color=lastChunkLineColor,
            width=1,
            dash='dot')), row=row, col=col)
    
        fig.add_trace(go.Scatter(x=chunk_df.index.values, y=chunk_df["LR"],
                          showlegend=False,
                          mode='lines',
                          line=dict(
                        color=lastChunkLineColor,
                        width=1,
                        dash='dot'),
                        fill='tonexty',
                        fillcolor=lastChunkFillColor), row=row, col=col)
                
    
    #%% BridgeBands/Trend
    
    
    # fig.add_trace(go.Scatter(x=df.index.values, y=df["close"].shift(63),
    #                          mode='lines',
    #                          line=dict(color="#ffff1c", width=1),
    #                          opacity = .5,
    #                          name='3M Mtum',
    #                          legendgroup="Main"), row=row, col=col)
     
    fig.add_trace(go.Scatter(x=df.index.values, y=df["close"].shift(21),
                             showlegend=showLegend,
                             mode='lines',
                             line=dict(color="#00c3ff", width=2),
                             opacity = .6,
                             name='1M Mtum',
                             legendgrouptitle_text="Main",
                             legendgroup="Main"), row=row, col=col)
    
    fig.add_trace(go.Candlestick(
        x=df.index.values,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        showlegend=False,
    ), row=row, col=col)

def getCharts(asset, lookback):
    df = asset.price_data.iloc[-lookback:].copy()
    
    isPercent = False
    
    if asset.ticker in ac.tickerLookup:
        if "isPercent" in ac.tickerLookup[asset.ticker]:
            isPercent = True
    
    layout = {
        "template": "plotly_dark",
        "xaxis_rangeslider_visible": False,
        "margin": {"r": 10, "t": 10, "l": 10, "b": 10},
        "legend": {
            "x": 1.075,
            "y": .95,
        }, 
    }

    layout_fig = go.Figure(layout=layout)
    
    noVolume = asset.ticker in ac.noVolumeTickers
    
    row_count = 3 if noVolume else 4
    row_heights = [.7, .15, .15] if noVolume else [.6, .13, .13, .14]
    subplot_titles = ("Price, Trend & Range", "Matrix", "Crowding") if noVolume else ("Price, Trend & Range", "Volume", "Matrix", "Crowding")
      
    fig = make_subplots(rows=row_count, cols=1, row_heights = row_heights, figure = layout_fig,
                        subplot_titles=subplot_titles, vertical_spacing=0.05)

    
    #Main Chart
    drawCandlestickChart(fig, df, isPercent, 1, 1)
    
    if asset.Stop > 0.0:
        fig.add_trace(go.Scatter(x=df.index.values, y=df["stop"],
                                  mode='lines',
                                  line=dict(color=chartSolidRed, width=2, dash = "dash"),
                                  name='Stop',
                                  legendgroup="Main"), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df.index.values, y=df["target"],
                                  mode='lines',
                                  line=dict(color=chartSolidGreen, width=2, dash = "dash"),
                                  name='Target',
                                  legendgroup="Main"), row=1, col=1)
    
    #%% Volume Chart
    if not noVolume:
        fig.add_trace(go.Scatter(x=df.index.values, y=df["Volume1M"],
                                 mode='lines',
                                 line=dict(color="#ffff1c", width=2),
                                 name='1M Avg',
                                 legendgroup="Volume"), row=2, col=1)
        
        fig.add_trace(go.Scatter(x=df.index.values, y=df["Volume1W"],
                                 mode='lines',
                                 line=dict(color="#00c3ff", width=2),
                                 name='1W Avg',
                                 legendgrouptitle_text="Volume",
                                 legendgroup="Volume"), row=2, col=1)
        
        addUpVolume(fig, df, "Absolute", 3.0, 2, 1)
        addUpVolume(fig, df, "Strong", 2.0, 2, 1)
        addUpVolume(fig, df, "Moderate", 1.0, 2, 1)
        addUpVolume(fig, df, "Weak", 0.0, 2, 1)
        
        addDownVolume(fig, df, "Absolute", -3.0, 2, 1)
        addDownVolume(fig, df, "Strong", -2.0, 2, 1)
        addDownVolume(fig, df, "Moderate", -1.0, 2, 1)
        addDownVolume(fig, df, "Weak", 0.0, 2, 1)
        
        fig.update_xaxes({"showgrid": True}, row=2, col=1)
        
        fig.update_yaxes({
                "title": {"text": "Volume", "standoff": 25},
                "side": "right",
                "tickprefix": "     ",
                "type": "log"
            }, row=2, col=1)
    #%% Volume Chart
    
    #%% Matrix Chart
    matrix_row = 2 if noVolume else 3
    
    fig.add_trace(go.Bar(
        x=df.index.values,
        y=df["Matrix_wvf_plot"],
        marker_color=df["Matrix_wvf_color"].tolist(),
        showlegend = False,
        width = 86400000
    ), row=matrix_row, col=1)
    
    fig.add_trace(go.Bar(
        x=df.index.values,
        y=df["Matrix_action"],
        marker_color=df["Matrix_action_color"].tolist(),
        showlegend = False,
        width = 86400000
    ), row=matrix_row, col=1)
    
    # fig.add_trace(go.Scatter(x=df.index.values, y=df["Matrix_UPshape"],
    #                           mode='markers',
    #                           marker=dict(symbol='cross', size = 6, color = "white"),
    #                           showlegend = False),
    #               row=matrix_row, col=1)
    
    # fig.add_trace(go.Scatter(x=df.index.values, y=df["Matrix_DOWNshape"],
    #                           mode='markers',
    #                           marker=dict(symbol='cross', size = 6, color = "white"),
    #                           showlegend = False),
    #               row=matrix_row, col=1)
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["Matrix_UPshape"],
                              mode='lines',
                              line=dict(color="white", width=6, dash="dot"),
                              showlegend = False),
                  row=matrix_row, col=1)
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["Matrix_DOWNshape"],
                              mode='lines',
                              line=dict(color="white", width=6, dash="dot"),
                              showlegend = False),
                  row=matrix_row, col=1)
    
    
    fig.add_trace(go.Candlestick(
        x=df.index.values,
        open=df['Matrix_Oo'],
        high=df['Matrix_Hh'],
        low=df['Matrix_Ll'],
        close=df['Matrix_Oo'],
        increasing_line_width = 4,
        decreasing_line_width = 4,
        showlegend = False,
    ), row=matrix_row, col=1)
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["Matrix_ob"],
                              mode='lines',
                              line=dict(color="gray", width=2, dash = "dash"),
                              showlegend = False), row=matrix_row, col=1)
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["Matrix_os"],
                              mode='lines',
                              line=dict(color="gray", width=2, dash = "dash"),
                              showlegend = False), row=matrix_row, col=1)
    
    fig.update_xaxes(row=matrix_row, col=1, rangeslider_visible=False)
    
    fig.update_yaxes({
            "title": {"text": "Matrix", "standoff": 25},
            "side": "right",
            "tickprefix": "     ",
            'showgrid': False
        }, row=matrix_row, col=1)
    
    #%% Matrix Chart
    
    #%% Crowding Chart
    crowding_row = 3 if noVolume else 4
    
    # portUtils.get_cmap_value(volume["VolumeEnum"], -3, 1, 'Reds', True)
    
    # fig.add_trace(go.Bar(
    #     x=df.index.values,
    #     y=df["crowding_score"],
    #     marker_color = df["crowding_color"].values,
    #     showlegend = False
    # ), row=crowding_row, col=1)
    
    addCrowding(fig, df, "Trim Shorts", crowding_row, 1)
    addCrowding(fig, df, "Get Short", crowding_row, 1)
    addCrowding(fig, df, "Puke", crowding_row, 1)
    addCrowding(fig, df, "Trim Longs", crowding_row, 1)
    addCrowding(fig, df, "Get Long", crowding_row, 1)
    addCrowding(fig, df, "Squeeze", crowding_row, 1)
    
    
    fig.update_yaxes({
            "title": {"text": "Crowding", "standoff": 25},
            "range" : [-50.0, 100.0],
            "side": "right",
            "tickprefix": "     ",
            'showgrid': False,
            # "type": "log"
        }, row=crowding_row, col=1)
    
    #%%
    
    fig.layout.annotations[0].update(x=0.065)
    fig.layout.annotations[0].update(y=0.9875)
    
    if not noVolume:
        fig.layout.annotations[1].update(x=0.025)
    
    fig.layout.annotations[1 if noVolume else 2].update(x=0.025)
    fig.layout.annotations[2 if noVolume else 3].update(x=0.025)
    
    fig.update_layout(height=1100, barmode='overlay')
    
    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]),  # hide weekends
        ]
    )
    
    return dcc.Graph(figure=fig)

def getAssetStats(asset):
    table_header = [
        html.Thead(html.Tr([html.Th("Info", colSpan = 4, className="bg-primary font-weight-bolder text-center h5")]))
    ]
    
    isPercent = False
    
    if asset.ticker in ac.tickerLookup:
        if "isPercent" in ac.tickerLookup[asset.ticker]:
            isPercent = True

    weight = asset.Weight[0] if isinstance(asset.Weight,np.ndarray) else asset.Weight
    pnl = asset.PnL[0] if isinstance(asset.PnL,np.ndarray) else asset.PnL

    weightAndPnL = html.Tr([html.Td("Weight", style=tdLabelStyles), html.Td(f"{weight:.2%}"),
                    html.Td("PnL", style=tdLabelStyles), html.Td(f"{pnl:.2%}", style = {"color": greenColor if pnl > 0.0 else redColor})])
    
    rPosAndLast = html.Tr([html.Td("R Pos", style=tdLabelStyles), html.Td(f"{asset.RPos:.2f}", style = portUtils.get_single_cmap_style(asset.RPos, 0.0, 1.0, cmap='RdYlGn', reverse=False, low=0, high=0,
                                                   st_threshold_1=0.75, st_threshold_2=0.25, white_threshold_1=0.75, white_threshold_2=0.25)),
                    html.Td("Last", style=tdLabelStyles), html.Td(f"{asset.last/100.0:.2%}" if isPercent else f"${asset.last:.2f}")])
    
    stopStyle = {}
    if asset.Stop > 0.0:
        stopStyle["backgroundColor"] = portUtils.get_single_cmap_value([asset.Stop_Ratio], 0.0, 1.0, cmap='Stops')[0]
    
    targetStyle = {}
    if asset.Target > 0.0:
        targetStyle["backgroundColor"] = portUtils.get_single_cmap_value([asset.Target_Ratio], 0.0, 1.0, cmap='Targets')[0]
    
    # stopAndTarget = html.Tr([html.Td("Stop", style=tdLabelStyles), html.Td(f"${asset.Stop:.2f}", style = stopStyle),
    #                 html.Td("Target", style=tdLabelStyles), html.Td(f"${asset.Target:.2f}", style = targetStyle)])
    
    trendAndMomentum = html.Tr([html.Td("Trend", style=tdLabelStyles), html.Td(asset.TrendEmoji),
                    html.Td("Momentum", style=tdLabelStyles), html.Td(asset.MomentumEmoji)])
    
    lrAndTr = html.Tr([html.Td("LR", style=tdLabelStyles), html.Td(f"{asset.LR/100.0:.2%}" if isPercent else f"${asset.LR:.2f}"),
                    html.Td("TR", style=tdLabelStyles), html.Td(f"{asset.TR/100.0:.2%}" if isPercent else f"${asset.TR:.2f}")])
    
    volumeAndCrowding = html.Tr([html.Td("Volume", style=tdLabelStyles), html.Td(asset.VolumeDesc, style = portUtils.getVolumeStyle(asset)),
                    html.Td("Crowding", style=tdLabelStyles), html.Td(asset.Crowding_Text, style = {"color": asset.Crowding_TextColor, "backgroundColor": asset.Crowding_Color})])
    
    volumeAndChg1D = html.Tr([html.Td("Chg 1D", style=tdLabelStyles), html.Td(f"{asset.Chg1D:.2%}", style = {"color": greenColor if asset.Chg1D > 0.0 else redColor}),
                              html.Td("Chg 1M", style=tdLabelStyles), html.Td(f"{asset.Chg1M:.2%}", style = {"color": greenColor if asset.Chg1M > 0.0 else redColor})])
    
    chg1MAndChg3M = html.Tr([html.Td("Chg 3M", style=tdLabelStyles), html.Td(f"{asset.Chg3M:.2%}", style = {"color": greenColor if asset.Chg3M > 0.0 else redColor}),
                             html.Td("", style=tdLabelStyles), html.Td("")])
    
    table_body = [html.Tbody([weightAndPnL, rPosAndLast,
                              # stopAndTarget,
                              lrAndTr, trendAndMomentum, volumeAndCrowding, volumeAndChg1D, chg1MAndChg3M])]
    
    table = dbc.Table(table_header + table_body, bordered=False, id="asset_stats_table", className = "white_table compact_table")
    
    return table

def getMiniChartTabs(asset):
    
    asset_crowding_tab_content = html.Div(getAssetCrowdingContent(asset))
    
    correlation_tab_content = html.Div(getCorrelationContent(asset))
    
    asset_recent_changes_tab_content = html.Div(getAssetRecentChanges(asset))
    
    tabs = dbc.Tabs(
        [
            dbc.Tab(asset_crowding_tab_content, tab_id="crowding_tab", label="Crowding"),
            dbc.Tab(correlation_tab_content, tab_id="correlations_tab", label="Correlations"),
            dbc.Tab(asset_recent_changes_tab_content, tab_id="asset_recent_changes_tab", label="Recent Changes", ),
        ],
        active_tab="crowding_tab"
    )
    
    return tabs

def getPositionMgmtCalcTabContent(asset):
    
    table_header = [
        html.Thead(html.Tr([html.Th("Position Management Calculator", colSpan = 1, className="bg-success font-weight-bolder text-center h5")]))
    ]
    
    rows = []
    
    rows.append(html.Tr(html.Td(getPositionMgmtCalc(asset), id="position_mgmt_calc_wrapper", colSpan = 1)))
    
    table_body = [html.Tbody(rows)]
    
    position_mgmt_calc_table = dbc.Table(table_header + table_body, bordered=False, id="position_mgmt_calc_table", className="white_table compact_table")
    
    return position_mgmt_calc_table

def getPositionMgmtCalc(asset):
    form = dbc.Container(
        fluid=True,
        children=[dbc.Row(
            [
                dbc.Col(dbc.Label(
                    "Vol Lookback (Years)", html_for="uxInput_Years"), width=3, className="pt-2 font-weight-bold"),
                dbc.Col(
                    dcc.Input(
                        id="uxInput_Years",
                        type="number",
                        min=.25, max=20.0, step=.25, value=3,
                        className="mt-1 w-100"
                    ), width=3
                ),
                dbc.Col(dbc.Label("Max Loss"), width=3, className="pt-2 font-weight-bold"),
                dbc.Col(
                    dcc.Input(
                        id="uxInput_MaxLoss",
                        type="number",
                        min=.25, max=10.0, step=.25, value=2.0,
                        className="mt-1 w-100"
                    ), width=3
                ),
                # dbc.Col(dbc.Button("Update", color="primary", id="uxButton_position_mgmt_calc", n_clicks=0), width = 2),
            ],
            className="g-2",
        ),
            dbc.Row(
                [
                    dbc.Col(dbc.Label(
                        "Stop Loss Sigma", html_for="uxInput_StopLossSigma"), width=3, className="pt-2 font-weight-bold"),
                    dbc.Col(
                        dcc.Input(
                            id="uxInput_StopLossSigma",
                            type="number",
                            min=.25, max=10.0, step=.25, value=1.5,
                            className="mt-1 w-100"
                        ), width=3
                    ),
                    dbc.Col(dbc.Label("Profit Target Sigma", html_for="uxInput_ProfitTargetSigma"), width=3, className="pt-2 font-weight-bold"),
                    dbc.Col(
                        dcc.Input(
                            id="uxInput_ProfitTargetSigma",
                            type="number",
                            min=.25, max=10.0, step=.25, value=2.25,
                            className="mt-1 w-100"
                        ), width=3
                    ),
                    # dbc.Col(dbc.Button("Update", color="primary", id="uxButton_position_mgmt_calc", n_clicks=0), width = 2),
                ],
                className="g-2",
            ),
            dbc.Row(
                [
                    dbc.Col(getPositionMgmtTable(asset, 3.0, 2.0, 1.5, 2.25), width=12, id="uxCol_PositionMgmtTable")

                ],
                className="g-2",

        ),
        dcc.Input(type="hidden", id="uxHidden_PositionMgmtCalc_Ticker", value=asset.ticker)
        ]
    )

    return form

def getPositionMgmtTable(asset, years, max_loss, stop_loss_sigma, profit_target_sigma):
    values = asset.calcPositionSizeValues(portfolio.portfolio_value, years, max_loss, stop_loss_sigma, profit_target_sigma)
    
    rows = []
    
    rows.append(html.Tr([html.Td("Monthly Vol", className="font-weight-bold"),
                        html.Td("Max Loss", className="font-weight-bold"),
                        html.Td("Target Gain", className="font-weight-bold")]))
    
    rows.append(html.Tr([html.Td(f"{values['monthly_vol']:.2%}"),
                        html.Td(f"{values['max_loss']:.2%}", ),
                        html.Td(f"{values['target_gain']:.2%}", )]))
    
    rows.append(html.Tr([html.Td("Shares", className="font-weight-bold"),
                        html.Td("Current Price", className="font-weight-bold"),
                        html.Td("Notional Value", className="font-weight-bold")]))
    
    rows.append(html.Tr([html.Td(f"{values['shares']}"),
                        html.Td(f"${values['current_price']:,.2f}"),
                        html.Td(f"${values['notional_value']:,.2f}")]))
    
    # if direction == "Long":
    rows.append(html.Tr([html.Td("Stop Price", className="font-weight-bold", style = {"backgroundColor": redColor}),
                        html.Td("Current Price", className="font-weight-bold"),
                        html.Td("Target Price", className="font-weight-bold", style = {"backgroundColor": greenColor})]))
    
    rows.append(html.Tr([html.Td(f"${values['long_stop_loss_value']:,.2f}"),
                        html.Td(f"${values['current_price']:,.2f}"),
                        html.Td(f"${values['long_profit_target_value']:,.2f}")]))
    # else:
    #     rows.append(html.Tr([html.Td("Target Price", className="font-weight-bold", style = {"backgroundColor": greenColor}),
    #                         html.Td("Current Price", className="font-weight-bold"),
    #                         html.Td("Stop Price", className="font-weight-bold", style = {"backgroundColor": redColor})
    #                         ]))
        
    #     rows.append(html.Tr([html.Td(f"${values['short_profit_target_value']:,.2f}"),
    #                         html.Td(f"${values['current_price']:,.2f}"),
    #                         html.Td(f"${values['short_stop_loss_value']:,.2f}")]))
        
    # if direction == "Long":
    rows.append(html.Tr([html.Td("Stop Ptg", className="font-weight-bold"),
                        html.Td(""),
                        html.Td("Target Ptg", className="font-weight-bold")]))
    
    rows.append(html.Tr([html.Td(f"{values['stop_loss_ptg']:.2%}"),
                        html.Td(""),
                        html.Td(f"{values['profit_target_ptg']:.2%}")]))
    # else:
    #     rows.append(html.Tr([html.Td("Target Ptg", className="font-weight-bold"),
    #                         html.Td(""),
    #                         html.Td("Stop Ptg", className="font-weight-bold")
    #                         ]))
        
    #     rows.append(html.Tr([html.Td(f"{values['profit_target_ptg']:.2%}"),
    #                         html.Td(""),
    #                         html.Td(f"{values['stop_loss_ptg']:.2%}")]))
    
    table_body = [html.Tbody(rows)]
    
    return dbc.Table(table_body, bordered=False, className="white_table compact_table")

def getAssetCrowdingContent(asset):
    
    table_header = [
        html.Thead(html.Tr([html.Th("Crowding", colSpan = 1, className="bg-danger font-weight-bolder text-center h5")]))
    ]
    
    rows = []
    
    rows.append(html.Tr(html.Td(getAssetCrowdingChart(asset), id="asset_crowding_chart_wrapper", colSpan = 1)))
    
    table_body = [html.Tbody(rows)]
    
    asset_crowding_table = dbc.Table(table_header + table_body, bordered=False, id="asset_crowding_table", className="white_table compact_table")
    
    return asset_crowding_table

def getAssetCrowdingChart(asset):
    
    content = ""
    
    lookback = 10
    
    if (not np.isnan(asset.IV_Premium) and not np.isnan(asset.IV_Skew)):
        layout = {
            "template": "plotly_dark",
            "xaxis_rangeslider_visible": False,
            "margin": {"r": 10, "t": 10, "l": 10, "b": 10},
            "title": {
                'text': f"{asset.ticker}",
                'y':0.925,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        }
        
        layout_fig = go.Figure(layout=layout)
        
        # subplot_titles = (f"{asset.ticker} - {asset.price_data.index.values[-1]}")
        # subplot_titles = (f"{asset.ticker}")

        fig = make_subplots(rows=1, cols=1, row_heights = [1.0], figure = layout_fig,
                            # subplot_titles=subplot_titles,
                            vertical_spacing=0.05)
        
        
        
        
        # fig.update_yaxes({
        #         "title": {"text": "Price", "standoff": 25},
        #         "tickformat": ".2f",
        #         "side": "right",
        #         "tickprefix": "      " if isPercent else "     $",
        #         "ticksuffix": "%" if isPercent else ""
        #     }, row=row, col=col)
        
        # self.price_data["iv_premium"] = self.price_data["put_iv"] / hvMean - 1.0
        # self.price_data["skew_zscore"] = technicals.calcZScore(self.price_data, "skew", 251)
        
        
        
        x_list = asset.price_data["skew_zscore"].tolist()
        x_list = [x for x in x_list if np.isnan(x) == False]
        x_list = x_list[-lookback:]
        
        y_list = asset.price_data["iv_premium"].tolist()
        y_list = [y * 100.0 for y in y_list if np.isnan(y) == False]
        y_list = y_list[-lookback:]
        
        if ((len(x_list) == 0) or (len(x_list) != len(y_list))):
            return "No data:("
        
        colors_range = range(lookback)
        colors_df = pd.DataFrame({
            "i": colors_range
            })
        
        iv_colors = portUtils.get_cmap_value(colors_df["i"], 0, 9, 'Crowding', False)
        
        marker_sizes = []
        for i in range(lookback):
            marker_sizes.append(5 + (i * 2))
        
        iv_colors = [ele for ele in reversed(iv_colors)]
        
        fig.add_trace(go.Scatter(x = x_list, y = y_list,
                                 mode='markers+lines',
                                 marker=dict(symbol='circle', size = marker_sizes, color = iv_colors),
                                 opacity= 1,
                                 line_color="#D3D3D3",
                                 line_width=1,
                                 line_shape="spline",
                                 showlegend = False,
                                 hovertemplate =
                                '<b>Skew</b>: %{x:.2f}'+
                                '<br><b>IV PD</b>: %{y:.0f}%<br>',
                                 # hoverinfo="text",
                                 # hovertext="test"
                                 ),
                      row=1, col=1)
        
        x_max = max([abs(min(x_list)), max(x_list)])
        y_max = max([abs(min(y_list)), max(y_list)])
        
        fig.update_xaxes({
            "range" : [-x_max * 1 - .5, x_max + .5],
            "dtick": .5,
            "zerolinewidth": 3,
            "zerolinecolor": "#91a3b0",
            "title": "Skew Z-Score",
            "tickfont": {
                "size": 14
                },
            "ticklabelstep": 2
            }, row=1, col=1)
        
        fig.update_yaxes({
            "range" : [-y_max - 10, y_max + 10],
            "dtick": 10,
            "tick0": 0,
            # "ticklabelstep": 0,
            "zerolinewidth": 3,
            "zerolinecolor": "#91a3b0",
            "title": "IV Premium/Discount",
            "ticksuffix": "%",
            "tickfont": {
                "size": 14
                }
            }, row=1, col=1)
        
        
        # fig.update_xaxes({
        #         "title": {"text": "CATS", "standoff": 25},
        #         "side": "right",
        #         "tickprefix": "     ",
        #         'showgrid': False
        #     }, row=1, col=1)
        
        # fig.layout.annotations[0].update(x=0.065)
        # fig.layout.annotations[0].update(y=1.99)
        
        fig.update_layout(height=320)
        
        
        content = dcc.Graph(figure=fig)
    else:
        content = "No data:("
    
    return content

def getCorrelationContent(asset):
    
    table_header = [
        html.Thead(html.Tr([html.Th("Correlations", colSpan = 8, className="bg-warning font-weight-bolder text-center h5")]))
    ]
    
    header_row = html.Tr([html.Th("Tick"),
                         html.Th("1W"),
                         html.Th("1M"),
                         html.Th("3M"),
                         html.Th("6M"),
                         html.Th("Trd"),
                         html.Th("Mtum"),
                         html.Th("R Pos")],
                        className = "font-weight-bold",
                        style = {"backgroundColor": "#15191E",
                                 "fontSize": "1.1em"})
    
    rows = []
    rows.append(header_row)
    
    index = 0
    maxCorr = 0.0
    maxCorrTicker = ""
    
    # print(asset.ticker)
    
    for ticker in ac.correlationTickers:
        # print(asset.ticker)
        
        corrAsset = allAssets[ticker]
        # print(corrAsset.ticker)
        w1Corr = getCorrelation(asset, corrAsset, 5)
        m1Corr = getCorrelation(asset, corrAsset, 21)
        m3Corr = getCorrelation(asset, corrAsset, 63)
        m6Corr = getCorrelation(asset, corrAsset, 126)
        
        if abs(m1Corr) > maxCorr:
            maxCorr = abs(m1Corr)
            maxCorrTicker = ticker
        
        rows.append(html.Tr([html.Td(ticker, className = "font-weight-bold", id = {
            "type": "ticker-corr",
            "index": index
            }),
            html.Td(f"{w1Corr:.2f}", style = portUtils.get_single_cmap_style(w1Corr, -1.0, 1.0, cmap='RdYlGn', reverse=False, low=0, high=0,
                  st_threshold_1=0.5, st_threshold_2=-0.5, white_threshold_1=0.5, white_threshold_2=-0.5)
                    ),
            html.Td(f"{m1Corr:.2f}", style = portUtils.get_single_cmap_style(m1Corr, -1.0, 1.0, cmap='RdYlGn', reverse=False, low=0, high=0,
                  st_threshold_1=0.5, st_threshold_2=-0.5, white_threshold_1=0.5, white_threshold_2=-0.5)
                    ),
            html.Td(f"{m3Corr:.2f}", style = portUtils.get_single_cmap_style(m3Corr, -1.0, 1.0, cmap='RdYlGn', reverse=False, low=0, high=0,
                  st_threshold_1=0.5, st_threshold_2=-0.5, white_threshold_1=0.5, white_threshold_2=-0.5)
                    ),
            html.Td(f"{m6Corr:.2f}", style = portUtils.get_single_cmap_style(m6Corr, -1.0, 1.0, cmap='RdYlGn', reverse=False, low=0, high=0,
                  st_threshold_1=0.5, st_threshold_2=-0.5, white_threshold_1=0.5, white_threshold_2=-0.5)
                    ),
            html.Td(corrAsset.TrendEmoji, className = "text-center"),
            html.Td(corrAsset.MomentumEmoji, className = "text-center"),
            html.Td(f"{corrAsset.RPos:.2f}", style = portUtils.get_single_cmap_style(corrAsset.RPos, 0.0, 1.0, cmap='RdYlGn', reverse=False, low=0, high=0,
                   st_threshold_1=0.75, st_threshold_2=0.25, white_threshold_1=0.75, white_threshold_2=0.25)),
             ],
            style = {"backgroundColor": "#272727"}))
        
        index += 1
    
    if maxCorrTicker in allAssets:
        rows.append(html.Tr(html.Td(getCorrelationChart(allAssets[maxCorrTicker]), id="correlation_chart_wrapper", colSpan = 8)))
    
    table_body = [html.Tbody(rows)]
    
    correlation_stats_table = dbc.Table(table_header + table_body, bordered=False, id="correlation_stats_table", className="white_table compact_table")
    
    return correlation_stats_table

def getCorrelation(asset1, asset2, length):
    return 1.0
    # x = asset1.price_data['Chg1D'].values[-length:]
    # y = asset2.price_data['Chg1D'].values[-length:]
    
    # if x.size != y.size:
    #     return np.nan
    
    # correlation, p_value = pearsonr(x, y)
    
    # return correlation

def getCorrelationChart(asset):
    df = asset.price_data.iloc[-63:].copy()
    
    isPercent = False
    
    if asset.ticker in ac.tickerLookup:
        if "isPercent" in ac.tickerLookup[asset.ticker]:
            isPercent = True
    
    layout = {
        "template": "plotly_dark",
        "xaxis_rangeslider_visible": False,
        "margin": {"r": 10, "t": 10, "l": 10, "b": 10},
        "title": {
            'text': asset.ticker,
            'y':0.925,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    }
    
    layout_fig = go.Figure(layout=layout)
    
    subplot_titles = (asset.ticker)

    fig = make_subplots(rows=1, cols=1, row_heights = [1.0], figure = layout_fig,
                        subplot_titles=subplot_titles, vertical_spacing=0.05)
    
    drawCandlestickChart(fig, df, isPercent, 1, 1, False)
    
    fig.layout.annotations[0].update(x=0.065)
    fig.layout.annotations[0].update(y=1.99)
    
    fig.update_layout(height=250)
        
    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]),  # hide weekends
        ]
    )
    
    return dcc.Graph(figure=fig)

def getAssetRecentChanges(asset):
    # dbc.CardHeader("Card header"),
    
    recentChangesCard = dbc.Card(
        [dbc.CardHeader(html.H5("Recent Changes", className="mb-0", style=dict(fontWeight = 700)),
                        className="bg-info text-white text-center", style=dict(paddingTop = ".35rem", paddingBottom = ".35rem")),
    dbc.CardBody(
        dbc.ListGroup(
            ac.getMfrChangeListGroupItemsForTicker(asset.ticker, amc),
            flush=True,
            style=dict(height = "243px", overflow = "auto")
            ),
        className = "p-0"
        )], className = "pb-3"
    )
    
    # table_header = [
    #     html.Thead(html.Tr([html.Th("Recent Changes", className="bg-info font-weight-bolder text-center h5")]))
    # ]
    
    # rows = []
    
    # recentChanges = dbc.ListGroup(
    #     ac.getMfrChangeListGroupItemsForTicker(asset.ticker, amc),
    # )
    
    # rows.append(html.Tr(html.Td(recentChanges)))

    # table_body = [html.Tbody(rows)]
    
    # recent_changes_table = dbc.Table(table_header + table_body, bordered=False, className="white_table compact_table", style=dict(height = "284px", overflow = "auto"))
    
    return recentChangesCard

def getAssetModalContent(asset):
    content = dbc.Row(
        [
            dbc.Col(
                getCharts(asset, 189),
                xs=8,
                className="dbc_dark"
            ),
            dbc.Col([
                dbc.Row(
                    [
                        dbc.Col(
                            getAssetStats(asset),
                            xs=12,
                            className="dbc_dark"
                        )]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            getMiniChartTabs(asset),
                            xs=12,
                            className="dbc_dark"
                        )]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            getPositionMgmtCalcTabContent(asset),
                            xs=12,
                            className="dbc_dark"
                        )]
                )
            ],
                xs=4
            )],
        className="dbc_dark"
    )
    
    return content

def getPerformanceChartTable(statistic, display_name, header_class, multiplier = 1.0, isPercent = False, lookback = 0):
    table_header = [
        html.Thead(html.Tr([html.Th(display_name, className=f"{header_class} font-weight-bolder text-center h5")]))
    ]
    
    layout = {
            "template": "plotly_dark",
            "xaxis_rangeslider_visible": False,
            "margin": {"r": 10, "t": 10, "l": 10, "b": 10},
            "legend": {"x": 0.35, "y": 1.2, "orientation": "h"}
        }
        
    layout_fig = go.Figure(layout=layout)
    
    fig = make_subplots(rows=1, cols=1, row_heights = [1.0], figure = layout_fig,
                        # subplot_titles=subplot_titles,
                        vertical_spacing=0.05)
    
    fig.update_yaxes({
                "title": {"standoff": 25},
                "tickformat": ".2f",
                "side": "right",
                "tickprefix": "      " if isPercent else "      ",
                "ticksuffix": "%" if isPercent else ""
            }, row=1, col=1)
    
    x_values = performanceDict["Portfolio"].index.values[-lookback:] if lookback != 0 else performanceDict["Portfolio"].index.values
    
    palette = cycle(px.colors.qualitative.D3)
    
    addPerformanceTrace(fig, x_values, "Portfolio", statistic, multiplier, next(palette), lookback)
    
    for key in performanceDict:
        if key != "Portfolio":
            addPerformanceTrace(fig, x_values, key, statistic, multiplier, next(palette), lookback)
    
    fig.update_layout(height=295)
    
    chart = dcc.Graph(figure=fig)
    
    chart_row = html.Tr([html.Td(chart, style=tdLabelStyles)])
    
    table_body = [html.Tbody([chart_row])]
    
    table = dbc.Table(table_header + table_body, bordered=False, className = "white_table compact_table p-0")
    
    return table

def addPerformanceTrace(fig, x_values, key, statistic, multiplier, color, lookback):
    
    fig.add_trace(go.Scatter(x=x_values, y=(performanceDict[key][statistic][-lookback:] if lookback != 0 else performanceDict[key][statistic]) * multiplier,
                              mode='lines',
                              line=dict(width=2, color = color),
                              showlegend = True,
                              name=key), row=1, col=1)
    
    
def getPerformanceStatsTable():
    table_header = [
        html.Thead(html.Tr([html.Th("Stats", colSpan = 4, className="bg-primary font-weight-bolder text-center h5")]))
    ]
    
    portfolio_stats = perf.getPerformanceStatsDict(performanceDict["Portfolio"])
    
    valueAndPeakEquity = html.Tr([html.Td("Value", style=tdLabelStyles), html.Td(f"${portfolio_stats['Value']:,.2f}"),
                    html.Td("Peak Equity", style=tdLabelStyles), html.Td(f"${portfolio_stats['PeakEquity']:,.2f}")])
    
    pnLAndAvgDailyPnl = html.Tr([html.Td("PnL", style=tdLabelStyles), html.Td(f"{portfolio_stats['PnL']:.2%}"),
                    html.Td("Avg Daily PnL", style=tdLabelStyles), html.Td(f"{portfolio_stats['AvgDailyPnL']:.2%}")])
    
    currentDDAndMaxDD = html.Tr([html.Td("Current Drawdown", style=tdLabelStyles), html.Td(f"{portfolio_stats['CurrentDrawdown']:.2%}"),
                    html.Td("Max Drawdown", style=tdLabelStyles), html.Td(f"{portfolio_stats['MaxDrawdown']:.2%}")])
    
    sharpeRatioAndSortinoRatio = html.Tr([html.Td("Sharpe Ratio", style=tdLabelStyles), html.Td(f"{portfolio_stats['SharpeRatio']:.2f}"),
                    html.Td("Sortino Ratio", style=tdLabelStyles), html.Td(f"{portfolio_stats['SortinoRatio']:.2f}")])
    
    calmarRatioAndGainPainRatio = html.Tr([html.Td("Calmar Ratio", style=tdLabelStyles), html.Td(f"{portfolio_stats['CalmarRatio']:.2f}"),
                    html.Td("Gain/Pain Ratio", style=tdLabelStyles), html.Td(f"{portfolio_stats['GainPainRatio']:.2f}")])
    
    table_body = [html.Tbody([valueAndPeakEquity, pnLAndAvgDailyPnl, currentDDAndMaxDD, sharpeRatioAndSortinoRatio, calmarRatioAndGainPainRatio])]
    
    table = dbc.Table(table_header + table_body, bordered=False, className = "white_table", style={"height": "351px", "fontSize": "1.4em"})
    
    return table

def getEurodollarTabContent():
    
    layout = {
            "template": "plotly_dark",
            "xaxis_rangeslider_visible": False,
            "margin": {"r": 10, "t": 10, "l": 25, "b": 25},
            "legend": {"x": 0.45, "y": 1.05, "orientation": "h"}
        }
        
    layout_fig = go.Figure(layout=layout)
    
    fig = make_subplots(rows=1, cols=1, row_heights = [1.0], figure = layout_fig,
                        # subplot_titles=subplot_titles,
                        vertical_spacing=0.05)
    
    fig.update_yaxes({
                "title": {"standoff": 25},
                "tickformat": ".2f",
                "side": "right",
                "tickprefix": "      ",
                "ticksuffix": "%"
            }, row=1, col=1)
    
    palette = cycle(px.colors.qualitative.D3)
    
    df = eurodollarCurveDf.loc[: '2027-1-1']
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["today"],
        mode='lines',
        line=dict(width=2, color = next(palette), shape="spline"),
        showlegend = True,
        name="Today"), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["1D"],
        mode='lines',
        line=dict(width=2, color = next(palette), shape="spline"),
        showlegend = True,
        name="1D"), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["1W"],
        mode='lines',
        line=dict(width=2, color = next(palette), shape="spline"),
        showlegend = True,
        name="1W"), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["1M"],
        mode='lines',
        line=dict(width=2, color = next(palette), shape="spline"),
        showlegend = True,
        name="1M"), row=1, col=1)
    
    fig.update_layout(height=1080)
    
    chart = dcc.Graph(figure=fig)
    
    content = dbc.Container(
        fluid=True,
        className="px-0",
        children=[dbc.Row(
        [
            dbc.Col(chart,
            xs=12,
            className="dbc_dark"
            )
            ]
        )])
    
    
    return content

    
    layout = {
            "template": "plotly_dark",
            "xaxis_rangeslider_visible": False,
            "margin": {"r": 10, "t": 10, "l": 25, "b": 25},
            "legend": {"x": 0.45, "y": 1.05, "orientation": "h"}
        }
        
    layout_fig = go.Figure(layout=layout)
    
    fig = make_subplots(rows=1, cols=1, row_heights = [1.0], figure = layout_fig,
                        # subplot_titles=subplot_titles,
                        vertical_spacing=0.05)
    
    fig.update_yaxes({
                "title": {"standoff": 25},
                "tickformat": ".2f",
                "side": "right",
                "tickprefix": "      $"
            }, row=1, col=1)
    
    palette = cycle(px.colors.qualitative.D3)
    
    df = oilCurveDf.loc[: '2027-1-1']
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["today"],
        mode='lines',
        line=dict(width=2, color = next(palette), shape="spline"),
        showlegend = True,
        name="Today"), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["1D"],
        mode='lines',
        line=dict(width=2, color = next(palette), shape="spline"),
        showlegend = True,
        name="1D"), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["1W"],
        mode='lines',
        line=dict(width=2, color = next(palette), shape="spline"),
        showlegend = True,
        name="1W"), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["1M"],
        mode='lines',
        line=dict(width=2, color = next(palette), shape="spline"),
        showlegend = True,
        name="1M"), row=1, col=1)
    
    fig.update_layout(height=1080)
    
    chart = dcc.Graph(figure=fig)
    
    content = dbc.Container(
        fluid=True,
        className="px-0",
        children=[dbc.Row(
        [
            dbc.Col(chart,
            xs=12,
            className="dbc_dark"
            )
            ]
        )])
    
    
    return content

def getPerformanceTabContent():
    lookback = 10
    
    content = dbc.Container(
        fluid=True,
        className="px-0",
        children=[dbc.Row(
        [
            dbc.Col([
                dbc.Row(
                    [
                        dbc.Col(
                            getPerformanceStatsTable(),
                            xs=6,
                            className="dbc_dark"
                        ),
                        dbc.Col(
                            html.Div(getPerformanceChartTable("AllTimePerformance", "Performance", "bg-success", 100.0, True)),
                            xs=6,
                            className="dbc_dark"
                        )]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(getPerformanceChartTable("SharpeRatio", "Sharpe Ratio", "bg-warning", lookback=lookback)),
                            xs=6,
                            className="dbc_dark"
                        ),
                        dbc.Col(
                            html.Div(getPerformanceChartTable("SortinoRatio", "Sortino Ratio", "bg-danger", lookback=lookback)),
                            xs=6,
                            className="dbc_dark"
                        )]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(getPerformanceChartTable("CalmarRatio", "Calmar Ratio", "bg-info", lookback=lookback)),
                            xs=6,
                            className="dbc_dark"
                        ),
                        dbc.Col(
                            html.Div(getPerformanceChartTable("GainPainRatio", "Gain/Pain Ratio", "bg-light", lookback=lookback)),
                            xs=6,
                            className="dbc_dark"
                        )]
                )
            ],
                xs=12
            )],
        className="dbc_dark"
    )])
    
    return content

app.layout = html.Div(
    [
     dcc.Store(id="asset_modal_store", data = {"collection": "", "active_ticker": ""}),
     dbc.Modal([
         dbc.ModalHeader("Test", id="asset-modal-header", className = "bg-info"),
         dbc.ModalBody(
             dbc.Container(
                 fluid=True,
                 children=getAssetModalContent(allAssets["SPY"]),
                 id="asset-modal-body"
             )
         ),
     ],
         id="asset_modal",
         size="xl",
         is_open=False,
     ),
     dbc.Container(
         fluid=True,
         className="px-0",
         children=[
             dbc.Navbar(
                 [
                     html.A(
                         # Use row and col to control vertical alignment of logo / brand
                         dbc.Row(
                             [
                                 dbc.Col(dbc.NavbarBrand(
                                     html.Div(html.Img(src=app.get_asset_url('logo.png'))),
                                     className="ml-2")),
                             ],
                             align="center",
                             no_gutters=True,
                         ),
                         href="#",
                     ),
                 ],
                 dark=True,
                 color="primary",
                 sticky="top"
             )
         ]),
     dbc.Container(
         fluid=True,
         children=[

             dbc.Row(
                 [dbc.Col(
                     get_side_bar(),
                     xs=3,
                     className="dbc_dark"
                 ),
                     dbc.Col(
                         dbc.Tabs(
                             [
                                 dbc.Tab([dbc.Alert("Click the table", id='out', className="pb-3", is_open = False),
                                      getAssetsDataTableWrapper("portfolio", portfolio, "bg-success"),
                                      getAssetsDataTableWrapper("watchlist", watchlist, "bg-danger")
                                      ], tab_id="portfolio_tab", label="Portfolio"),
                                 dbc.Tab(getPerformanceTabContent(), tab_id="performance_tab", label="Performance"),
                                 dbc.Tab(getEurodollarTabContent(), tab_id="eurodollar_tab", label="Eurodollar Curve"),
                                 dbc.Tab("The Macro Chart", tab_id="the_macro_chart", label="The Macro Chart"),
                                 ],
                             active_tab="portfolio_tab"
                         
                         ),
                     xs=9,
                     id="main_content"
                 )],
                 className="dbc_dark mt-4"
             )
         ])
     ])


@app.callback(
    (Output("uxCol_PositionMgmtTable", "children")),
    [Input('uxInput_Years', 'value'), Input('uxInput_MaxLoss', 'value'), Input('uxInput_StopLossSigma', 'value'), Input('uxInput_ProfitTargetSigma', 'value')],
    (State("uxHidden_PositionMgmtCalc_Ticker", "value"))
    )
def update_position_mgmt_calc(years, maxLoss, stop_loss_sigma, profit_target_sigma, ticker):

    return getPositionMgmtTable(allAssets[ticker], years, maxLoss, stop_loss_sigma, profit_target_sigma)

@app.callback(
    Output('correlation_chart_wrapper', 'children'),
    Input({'type': 'ticker-corr', 'index': ALL}, 'n_clicks'),
    State({'type': 'ticker-corr', 'index': ALL}, 'children')
    )
def update_correlation_chart(blah, c):
    ctx = dash.callback_context

    ticker = ""

    if len(ctx.triggered) > 0 and "ticker-corr" in ctx.triggered[0]['prop_id']:
        prop_id_dict = json.loads(ctx.triggered[0]['prop_id'].replace(".n_clicks", ""))
        ticker = c[prop_id_dict['index']]
        
    return dash.no_update if ticker == "" else getCorrelationChart(allAssets[ticker])

def get_next_nav_ticker(ticker_list, current_ticker):
    if "Cash" in ticker_list:
        ticker_list.remove('Cash')
        
    next_ticker = ""
    ticker_list_len = len(ticker_list)
    
    for i in range(ticker_list_len):
        t = ticker_list[i]
        
        if (t == current_ticker) and (i == (ticker_list_len - 1)):
            next_ticker = ticker_list[0]
        elif (t == current_ticker):
            next_ticker = ticker_list[i + 1]
            
    return next_ticker

def get_prev_nav_ticker(ticker_list, current_ticker):
    
    if "Cash" in ticker_list:
        ticker_list.remove('Cash')
    
    prev_ticker = ""
    ticker_list_len = len(ticker_list)
    
    for i in range(ticker_list_len):
        t = ticker_list[i]
        
        if (t == current_ticker) and (i == 0):
            prev_ticker = ticker_list[ticker_list_len - 1]
        elif (t == current_ticker):
            prev_ticker = ticker_list[i - 1]
            
    return prev_ticker

@app.callback(
    [Output('asset-modal-body', 'children'), Output('asset-modal-header', 'children'), Output('asset_modal', 'is_open'), Output("asset_modal_store", "data")],
    [Input("portfolio_assets_data_table", "active_cell"), Input("watchlist_assets_data_table", "active_cell"),
     Input({'type': 'nav_button', 'index': ALL}, 'n_clicks'), Input({'type': 'ticker-td', 'index': ALL}, 'n_clicks')],
    [State({'type': 'ticker-td', 'index': ALL}, 'children'), State("asset_modal_store", "data")]
    )
def update_asset_modal(portfolio_assets_data_table_active_cell, watchlist_assets_data_table_active_cell, nav_button,
                       blah, c, asset_modal_store_data):
    ctx = dash.callback_context

    ticker = ""
    collection = ""

    if len(ctx.triggered) > 0 and "portfolio_assets_data_table.active_cell" in ctx.triggered[0]['prop_id']:
        ticker = portfolio_assets_data_table_active_cell['row_id']
        collection = "portfolio"
    elif len(ctx.triggered) > 0 and "watchlist_assets_data_table.active_cell" in ctx.triggered[0]['prop_id']:
        ticker = watchlist_assets_data_table_active_cell['row_id']
        collection = "watchlist"
    elif len(ctx.triggered) > 0 and "ticker-td" in ctx.triggered[0]['prop_id']:
        prop_id_dict = json.loads(ctx.triggered[0]['prop_id'].replace(".n_clicks", ""))
        
        split = prop_id_dict['index'].split(":")
        ticker = c[int(split[0])]
        collection = split[1]
    elif len(ctx.triggered) > 0 and "nav_button" in ctx.triggered[0]['prop_id']:
        prop_id_dict = json.loads(ctx.triggered[0]['prop_id'].replace(".n_clicks", ""))
        isNext = prop_id_dict['index'] == 1
        
        ticker_list = ""
        collection = asset_modal_store_data["collection"]
        
        if collection == "portfolio":
            ticker_list = [*portfolio.collection]
        elif collection == "watchlist":
            ticker_list = [*watchlist.collection]
        elif collection == "potentials":
            ticker_list = [*potentials.collection]
        elif collection == "equities":
            ticker_list = [*equityTickers]
        elif collection == "bonds":
            ticker_list = [*bondTickers]
            
        if isNext:
            ticker = get_next_nav_ticker(ticker_list, asset_modal_store_data["active_ticker"])
        else:
            ticker = get_prev_nav_ticker(ticker_list, asset_modal_store_data["active_ticker"])
            
        
        
    renderModal = ticker != ""
    content = ""
    headerContent = ""
    
    if renderModal:
        
        asset = allAssets[ticker]
        
        content = getAssetModalContent(asset)
        
        headerContent = dbc.Container(
            fluid=True,
            className="px-0",
            children=dbc.Row(dbc.Col(
                html.Div([dbc.Button("Prev", id = {
                    "type": "nav_button",
                    "index": 0
                    }, className="me-2", color="primary", size="lg", n_clicks=0),
                          html.Div(f"{ticker} - Chart and Technicals"),
                          dbc.Button("Next", id = {
                              "type": "nav_button",
                              "index": 1
                              }, className="me-2", color="primary", size="lg", n_clicks=0)],
                         className="d-flex justify-content-between"), xs=12
            )))

    return content, headerContent, renderModal, {"collection": collection, "active_ticker": ticker}

if __name__ == '__main__':
    app.run_server(debug=(args.debug), port='5435')
