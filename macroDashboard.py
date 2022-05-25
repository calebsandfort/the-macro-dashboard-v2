# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 14:44:22 2021

@author: csandfort
"""
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import datetime
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
# df = pd.DataFrame({
#     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#     "Amount": [4, 1, 2, 2, 4, 5],
#     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
# })

# fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

big_board_assets = [
        {"ticker": "SPY", "display": "SPY"},
        {"ticker": "^VIX", "display": "VIX"},
        {"ticker": "QQQ", "display": "QQQ"},
        {"ticker": "^VXN", "display": "VXN"}
    ]

app.layout = html.Div(
    className="row",
    children=[
        # Interval component for live clock
        dcc.Interval(id="interval", interval=60 * 1000, n_intervals=0),
        dcc.Store(id='big-board-store'),
        html.Div(
            className="three columns div-left-panel",
            children=[
                html.Div(
                    className="div-info",
                    children=[
                        # html.A(
                        #     html.Img(
                        #         className="logo",
                        #         src=app.get_asset_url("dash-logo-new.png"),
                        #     ),
                        #     href="https://plotly.com/dash/",
                        # ),
                        html.H6(className="title-header",
                                children="MACRO DASHBOARD"),
                        dcc.Markdown(
                            """
                            This app continually queries Yahoo Finance and TD Ameritrade
                            to bring up to minute macro market information.
                            """
                        ),
                    ],
                ),
                # Big Board Div
                html.Div(
                    className="div-big-board",
                    children=[
                        html.P(
                            id="live_clock",
                            className="three-col",
                            children="",
                        ),
                        html.P(className="three-col", children="Last"),
                        html.P(className="three-col", children="%Chg"),
                        html.Div(
                            id="big-board-quotes",
                            className="div-big-board-quotes",
                        ),
                    ],
                )
            ]
        )

    ])

# Callback to update live clock
@app.callback(Output("big-board-store", "data"), [Input("interval", "n_intervals")])
def update_big_board_store(n):
    # big_board_df = pd.DataFrame(columns = ['Ticker', 'Last', 'Change'])
    
    tickers = []
    prices = []
    changes = []
    
    for asset in big_board_assets:
        tickers.append(asset["display"])
        prices.append(123.2)
        changes.append(.43)
     
    data = {
        "prices": prices,
        "changes": changes
        }   
     
    df = pd.DataFrame(data, tickers)   
     
    #print(df.to_json(date_format='iso', orient='split'))
    
    return df.to_json(date_format='iso', orient='split')

@app.callback(Output('big-board-quotes', 'children'), Input('big-board-store', 'data'))
def update_big_board(jsonified_big_board_data):
    dff = pd.read_json(jsonified_big_board_data, orient='split')
    quote_rows = []
    
    for ticker in dff.index.values:
        print(ticker)
        quote_rows.append(html.Div(
            className="rows",
            children=[
                html.P(
                    ticker,
                    className="three-col")
            ])
        )
    
    return quote_rows

@app.callback(Output("live_clock", "children"), [Input("interval", "n_intervals")])
def update_time(n):
    return datetime.datetime.now().strftime("%#I:%M %p")


if __name__ == '__main__':
    app.run_server(debug=True, port='1203')
