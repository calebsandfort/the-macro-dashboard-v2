# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 16:57:19 2022

@author: csandfort
"""
import dash
from dash import dash_table
from dash_table import DataTable, FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import datetime
from dash.dependencies import Input, Output, State
import dataRetrieval as dr
import portfolioUtilities as portUtils
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import constants
import assetClasses as ac

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

greenColor = "#77b300"
redColor = 'IndianRed'

chartSolidGreen = "#3D9970"
chartTransGreen = 'rgba(61,153,112,0.1)'
chartSolidRed = "#FF4136"
chartTransRed = 'rgba(255,65,54,0.1)'

portfolio = ac.AssetCollection("Portfolio.csv")

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
    dict(id='PnL', name='PnL', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='Chg1D', name='1D', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='Chg1M', name='1M', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='Chg3M', name='3M', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='BBPos', name='BB Pos', type='numeric',
         format={"specifier": ".2f"}),
    dict(id='VolumeDesc', name='Volume'),
    dict(id='TradeEmoji', name='Trade'),
    dict(id='TrendEmoji', name='Trend'),
    dict(id='IvPd', name='IV', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='IV1DΔ', name='IV 1DΔ', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='IV1WΔ', name='IV 1WΔ', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='IV1MΔ', name='IV 1MΔ', type='numeric',
         format={"specifier": ".2%"}),
    ])


    

    styles = []




    styles.extend(
        [{
            'if': {'column_id': 'TrendEmoji'},
            'textAlign': 'center'
        },
        {
            'if': {'column_id': 'TradeEmoji'},
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
        }])
    
    styles.extend(portUtils.get_column_cmap_values(assetCollection.df, 'BBPos', 0.0, 1.0, cmap='RdYlGn', reverse=False, low=0, high=0,
                                                   st_threshold_1=0.75, st_threshold_2=0.25, white_threshold_1=0.75, white_threshold_2=0.25))


    styles.append({
        'if': {
            'filter_query': '{Ticker} = "Cash"',
            'column_id': ["PnL", "Chg1D", "Chg1M", "Chg3M", "TrendEmoji", "TradeEmoji", "BBPos", "VolumeDesc"]
        },
        'color': 'transparent',
        'backgroundColor': 'rgb(39, 39, 39)'
    })

    assetsDataTable = DataTable(
        id="{}_assets_data_table".format(name.replace(" ", "_")),
        data=assetCollection.df.to_dict("records"),
        columns=columns,
        # hidden_columns=['Chg1D_zs', 'Chg1W_zs', 'Chg1M_zs', 'Chg3M', 'Chg3M_zs'],
        css=[{"selector": ".dash-spreadsheet-menu", "rule": "display: none"}],
        sort_action='native',
        style_header=data_table_style_header_dict,
        style_cell=data_table_style_cell_dict,
        style_data_conditional=styles
    )

    return assetsDataTable

app.layout = html.Div(
    [
     dbc.Modal([
         dbc.ModalHeader("Test", id="asset-modal-header", className = "bg-info"),
         dbc.ModalBody(
             dbc.Container(
                 fluid=True,
                 children=["asset-modal-body"],
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
                                     html.H4("The Macro™ Dashboard® V2"),
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
                     "side_bar",
                     xs=2,
                     className="dbc_dark"
                 ),
                     dbc.Col(
                         [dbc.Alert("Click the table", id='out', className="pb-3", is_open = True),
                          html.Div(get_assets_data_table("portfolio", portfolio), id="portfolio_data_table")
                          ],
                     xs=10,
                     id="main_content"
                 )],
                 className="dbc_dark mt-4"
             )
         ])
     ])


# @app.callback([Output("out", "children"), Output("portfolio_data_table", "children")],
#               Input('portfolio-store', 'data'))
# def portfolio_store_callback(data):
#     portfolio_data_table = get_assets_data_table("portfolio", data)
    
#     return "", portfolio_data_table
    

#     dbc.ModalHeader("Test", id="asset-modal-header", className = "bg-info"),
#     dbc.ModalBody(
#         dcc.Graph(id="asset-modal-candlestick-graph")
#     ),
# ],
#     id="asset_modal",

@app.callback(
    [Output('asset-modal-body', 'children'), Output('asset-modal-header', 'children'), Output('asset_modal', 'is_open')],
    Input("portfolio_assets_data_table", "active_cell")
    )
def update_asset_modal(active_cell):
    ticker = ""
    content = ""
    
    if active_cell is not None:
        ticker = active_cell['row_id']
        
        asset = portfolio.collection[ticker]
        
        content = dbc.Row(
            [
                dbc.Col(
                    getCandlestickChart(asset),
                    xs=8,
                    className="dbc_dark"
                ),
                dbc.Col([
                    dbc.Row(
                        [
                            dbc.Col(
                                "Stats",
                                xs=12,
                                className="dbc_dark"
                            )]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                "Correlation Chart",
                                xs=12,
                                className="dbc_dark"
                            )]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                "IVRVPD",
                                xs=12,
                                className="dbc_dark"
                            )]
                    )
                ],
                    xs=4
                )],
            className="dbc_dark"
        )

    return content, f"{ticker} - Chart and Technicals", True if active_cell is not None else False

def getCandlestickChart(asset):
    df = asset.price_data.iloc[-189:].copy()
    
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
    
    fig = make_subplots(rows=3, cols=1, row_heights = [.7, .15, .15], figure = layout_fig,
                        subplot_titles=("Price, Trend & Range", "Volume", "RVol"), vertical_spacing=0.05)

    fig.update_yaxes({
            "title": {"text": "Price", "standoff": 25},
            "tickformat": ".2f",
            "side": "right",
            "tickprefix": "     $"
        }, row=1, col=1)
    
    
    #Main Chart
    
    #%% BridgeBands/Trend
    idxs = df.index.values
    startIndex = idxs[0]

    for i in range(1, len(idxs)):

        if not pd.isna(df.at[df.index.values[i], "BullTrend"]) and pd.isna(df.at[df.index.values[i - 1], "BullTrend"]):

            df.at[df.index.values[i], "BearTrend"] = df.at[df.index.values[i], "Trend"]

            chunk_df = df[startIndex:df.index.values[i]]
            

            fig.add_trace(go.Scatter(x=chunk_df.index.values, y=chunk_df["BBTop"],
                                      showlegend=False,
                                      mode='lines',
                                      line=dict(
                color="FloralWhite",
                width=1,
                dash='dot')), row=1, col=1)

            fig.add_trace(go.Scatter(x=chunk_df.index.values, y=chunk_df["BBBot"],
                              showlegend=False,
                              mode='lines',
                              line=dict(
                            color="FloralWhite",
                            width=1,
                            dash='dot'),
                            fill='tonexty',
                            fillcolor=chartTransRed), row=1, col=1)
            
            startIndex = df.index.values[i]

        if not pd.isna(df.at[df.index.values[i], "BearTrend"]) and pd.isna(df.at[df.index.values[i - 1], "BearTrend"]):

            df.at[df.index.values[i], "BullTrend"] = df.at[df.index.values[i], "Trend"]
            
            chunk_df = df[startIndex:df.index.values[i]]
            
            fig.add_trace(go.Scatter(x=chunk_df.index.values, y=chunk_df["BBTop"],
                                      showlegend=False,
                                      mode='lines',
                                      line=dict(
                color="FloralWhite",
                width=1,
                dash='dot')), row=1, col=1)
    
            fig.add_trace(go.Scatter(x=chunk_df.index.values, y=chunk_df["BBBot"],
                              showlegend=False,
                              mode='lines',
                              line=dict(
                            color="FloralWhite",
                            width=1,
                            dash='dot'),
                            fill='tonexty',
                            fillcolor=chartTransGreen), row=1, col=1)
                
            startIndex = df.index.values[i]

    chunk_df = df[startIndex:df.index.values[-1]]
            
    fig.add_trace(go.Scatter(x=chunk_df.index.values, y=chunk_df["BBTop"],
                              showlegend=False,
                              mode='lines',
                              line=dict(
        color="FloralWhite",
        width=1,
        dash='dot')), row=1, col=1)

    fig.add_trace(go.Scatter(x=chunk_df.index.values, y=chunk_df["BBBot"],
                      showlegend=False,
                      mode='lines',
                      line=dict(
                    color="FloralWhite",
                    width=1,
                    dash='dot'),
                    fill='tonexty',
                    fillcolor=chartTransGreen if pd.isna(df.at[df.index.values[-1], "BearTrend"]) else chartTransRed), row=1, col=1)
                

    fig.add_trace(go.Scatter(x=df.index.values, y=df["BullTrend"],
                             mode='lines',
                             line=dict(color=chartSolidGreen, width=4),
                             name='🐮 Trend',
                             legendgrouptitle_text="Main",
                             legendgroup="Main"), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index.values, y=df["BearTrend"],
                             mode='lines',
                             line=dict(color=chartSolidRed, width=4),
                             name='🐷 Trend',
                             legendgroup="Main"), row=1, col=1)
    
    #%% BridgeBands/Trend
    
    #%% Trade
    
    startIndex = idxs[0]

    for i in range(1, len(idxs)):

        if not pd.isna(df.at[df.index.values[i], "BullTrade"]) and pd.isna(df.at[df.index.values[i - 1], "BullTrade"]):

            df.at[df.index.values[i], "BearTrade"] = df.at[df.index.values[i], "Trade"]
            
            startIndex = df.index.values[i]

        if not pd.isna(df.at[df.index.values[i], "BearTrade"]) and pd.isna(df.at[df.index.values[i - 1], "BearTrade"]):

            df.at[df.index.values[i], "BullTrade"] = df.at[df.index.values[i], "Trade"]       
                
            startIndex = df.index.values[i]
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["BullTrade"],
                             mode='lines',
                             line=dict(color=chartSolidGreen, width=2, dash='dash'),
                             name='🐮 Trade',
                             legendgroup="Main"), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index.values, y=df["BearTrade"],
                             mode='lines',
                             line=dict(color=chartSolidRed, width=2, dash='dash'),
                             name='🐷 Trade',
                             legendgroup="Main"), row=1, col=1)
    
    #%% Trade
       
    fig.add_trace(go.Candlestick(
        x=df.index.values,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        showlegend=False,
    ), row=1, col=1)
    
    #%% Volume Chart
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
    
    addUpVolume(fig, df, "Absolute", 3.0)
    addUpVolume(fig, df, "Strong", 2.0)
    addUpVolume(fig, df, "Moderate", 1.0)
    addUpVolume(fig, df, "Weak", 0.0)
    
    addDownVolume(fig, df, "Absolute", -3.0)
    addDownVolume(fig, df, "Strong", -2.0)
    addDownVolume(fig, df, "Moderate", -1.0)
    addDownVolume(fig, df, "Weak", 0.0)
    
    fig.update_xaxes({"showgrid": True}, row=2, col=1)
    
    fig.update_yaxes({
            "title": {"text": "Volume", "standoff": 25},
            "side": "right",
            "tickprefix": "     ",
            "type": "log"
        }, row=2, col=1)
    #%% Volume Chart
    
    fig.layout.annotations[0].update(x=0.065)
    fig.layout.annotations[0].update(y=0.9875)
    fig.layout.annotations[1].update(x=0.025)
    fig.layout.annotations[2].update(x=0.025)
    
    fig.update_layout(height=1000)
    
    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]),  # hide weekends
        ]
    )
    
    return dcc.Graph(figure=fig)

def addUpVolume(fig, df, name, enumValue):
    volume = df.loc[(df["IsUp"] == True) & (df["VolumeEnum"] == enumValue)]
    
    volume_colors = portUtils.get_cmap_value(volume["VolumeEnum"], -1, 3, 'Greens', False)
    
    fig.add_trace(go.Bar(x=volume.index.values, y=volume["volume"],
                showlegend=True,
                name=name,
                legendgroup="Volume",
                marker=dict(color= volume_colors)),
        row=2, col=1)
    
def addDownVolume(fig, df, name, enumValue):
    volume = df.loc[(df["IsUp"] == False) & (df["VolumeEnum"] == enumValue)]
    
    volume_colors = portUtils.get_cmap_value(volume["VolumeEnum"], -3, 1, 'Reds', True)
    
    fig.add_trace(go.Bar(x=volume.index.values, y=volume["volume"],
                showlegend=True,
                name=name,
                legendgroup="Volume",
                marker=dict(color= volume_colors)),
        row=2, col=1)

if __name__ == '__main__':
    app.run_server(debug=True, port='5435')
