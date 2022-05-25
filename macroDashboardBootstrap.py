# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 11:14:38 2021

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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

RV_BINS = 9

empty_data = portUtils.initializeData()
rosetta_stone = constants.grids

market_snapshot_assets = [
    {"ticker": "SPY", "display": "SPY"},
    {"ticker": "^VIX", "display": "VIX"},
    {"ticker": "Blank", "display": "Blank"},
    {"ticker": "QQQ", "display": "QQQ"},
    {"ticker": "^VXN", "display": "VXN"},
    {"ticker": "Blank", "display": "Blank"},
    {"ticker": "IWM", "display": "IWM"},
    {"ticker": "Blank", "display": "Blank"},
    {"ticker": "CL=F", "display": "Oil"},
    {"ticker": "^OVX", "display": "OVX"},
    {"ticker": "Blank", "display": "Blank"},
    {"ticker": "HG=F", "display": "Copper"},
    {"ticker": "NG=F", "display": "Nat Gas"},
    {"ticker": "BTC-USD", "display": "Bitcoin"},
    {"ticker": "ETH-USD", "display": "Ethereum"},
    {"ticker": "DX-Y.NYB", "display": "DXY"},
    {"ticker": "Blank", "display": "Blank"},
    {"ticker": "GLD", "display": "GLD"},
    {"ticker": "TLT", "display": "TLT"},
    {"ticker": "^TNX", "display": "TNX"},
    {"ticker": "^TYX", "display": "TYX"},
    {"ticker": "Blank", "display": "Blank"},
    {"ticker": "^KS11", "display": "Kospi"},
    {"ticker": "^N225", "display": "Nikkei"},
    {"ticker": "000001.SS", "display": "Shanghai"},
    {"ticker": "^GDAXI", "display": "DAX"},
]


def get_assets_data(assets):
    tickers = []
    displays = []
    prices = []
    changes = []
    previous_prices = []

    for asset in assets:
        tickers.append(asset["ticker"])
        displays.append(asset["display"])

        previous_prices.append(0.1)
        prices.append(0.1)
        changes.append(-0.0001)

    data = {
        "Ticker": displays,
        "Last": prices,
        "Change": changes,
        "Previous": previous_prices
    }

    df = pd.DataFrame(data, tickers)

    return df.to_json(date_format='iso', orient='split')


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


def getCardHeader(text, bg_class):
    return dbc.CardHeader(html.Div(text, className="card-header-font"),
                          className=f"bg-{bg_class} text-white",
                          )


def initMarketSnapshotDataTable():
    columns = [
        dict(id='Ticker', name='Ticker'),
        dict(id='Last', name='Last', type='numeric',
             format=FormatTemplate.money(2)),
        dict(id='Change', name='%Change', type='numeric',
             format={"specifier": "+.2%"}),
        dict(id='Previous', name='Previous',
             type='numeric', format={"specifier": "$.2f"})
    ]

    marketSnapshotDataTable = DataTable(
        id="market_snapshot_data_table",
        columns=columns,
        data=pd.read_json(get_assets_data(market_snapshot_assets),
                          orient='split').to_dict("records"),
        hidden_columns=['Previous'],
        css=[{"selector": ".dash-spreadsheet-menu", "rule": "display: none"}],
        # sort_action='native',
        style_header=data_table_style_header_dict,
        style_cell=data_table_style_cell_dict,
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{Change} > 0',
                    'column_id': ['Ticker', 'Change']
                },
                'color': greenColor
            },
            {
                'if': {
                    'filter_query': '{Change} < 0 and {Change} != -0.0001',
                    'column_id': ['Ticker', 'Change']
                },
                'color': redColor
            },
            {
                'if': {
                    'filter_query': '{Previous} > 0.1 and {Last} > {Previous}',
                    'column_id': ['Last']
                },
                'color': greenColor
            },
            {
                'if': {
                    'filter_query': '{Previous} > 0.1 and {Last} < {Previous}',
                    'column_id': ['Last']
                },
                'color': redColor
            },
            {
                'if': {
                    'filter_query': '{Ticker} = "Blank"'
                },
                'color': 'transparent'
            }
        ]
    )

    return marketSnapshotDataTable


side_bar = [
    dbc.Card(
        [
            getCardHeader("Market Snapshot", "info"),
            dbc.CardBody(
                [
                    html.Div(
                        initMarketSnapshotDataTable()
                    )
                ]
            ),
            dbc.CardFooter(
                [html.Small(id="market-snapshot-timestamp",
                           children=["test"], className="form-text"),
                 html.Div(
                 dbc.Button("ETH - BTC Comparison", id="open-eth-btc-comparison-modal", n_clicks=0, color="warning", size="lg", className="font-weight-bold"),
                     className="text-center py-3"
                 )
                 ],
                className="py-1"
            )
        ]
    )
]

goldilocksColor = "#00B050"
reflationColor = "#66FF66"
inflationColor = "#FF0000"
deflationColor = "#002060"


def get_assets_table(table_name, assets, is_portfolio = True):
    columns = [
        dict(id='Ticker', name='Ticker'),
        dict(id='Name', name='Name'),
        ]
    
    if is_portfolio:
        columns.extend([ dict(id='Weight', name='Weight', type='numeric',
             format={"specifier": ".2%"}),
        dict(id='PnL', name='P/L Open', type='numeric',
             format={"specifier": ".2%"}),
        ])
        
    columns.extend([dict(id='Last', name='Last', type='numeric',
         format={"specifier": "$.2f"}),
    dict(id='Chg1D', name='Chg 1D', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='Chg1W', name='Chg 1W', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='Chg1M', name='Chg 1M', type='numeric',
         format={"specifier": ".2%"}),
    dict(id='Chg3M', name='Chg 3M', type='numeric',
         format={"specifier": ".2%"}),
    
    dict(id='Chg1D_zs', name='Chg 1D ZS', type='numeric',
         format={"specifier": ".1f"}),
    dict(id='Chg1W_zs', name='Chg 1W ZS', type='numeric',
         format={"specifier": ".1f"}),
    dict(id='Chg1M_zs', name='Chg 1M ZS', type='numeric',
         format={"specifier": ".1f"}),
    dict(id='Chg3M_zs', name='Chg 3M ZS', type='numeric',
         format={"specifier": ".1f"}),
    
    
    dict(id='BBPos', name='BB Pos', type='numeric',
         format={"specifier": ".2f"}),
    dict(id='VolumeDesc', name='Volume'),
    dict(id='TradeEmoji', name='Trade'),
    dict(id='TrendEmoji', name='Trend'),
    dict(id='MomoEmoji', name='Momo'),

    

    dict(id='RV1M', name='RV 1M', type='numeric',
         format={"specifier": ".1f"}),
    dict(id='RV1W', name='RV 1W', type='numeric',
         format={"specifier": ".1f"}),
    dict(id='RV1D', name='RV 1D', type='numeric',
         format={"specifier": ".1f"}),
    dict(id='RV', name='RV', type='numeric',
         format={"specifier": ".1f"}),
    ])
        
        
        
        
        # dict(id='CostBasis', name='CB', type='numeric',
        #      format={"specifier": "$.2f"}),
        # dict(id='CurrentValue', name='CV', type='numeric',
        #      format={"specifier": "$.2f"}),
        # dict(id='Asset Class', name='Asset Class'),
        # dict(id='Factor', name='Factor/Sector'),
        # dict(id='Exposure', name='Cap/Exposure'),
        # dict(id='GRID', name='GRID')


    dff = pd.read_json(assets, orient='split') if type(assets) == str else assets

    dff["IsBullTrend"] = dff["Last"] > dff["Trend"]
    dff['TrendEmoji'] = dff['IsBullTrend'].apply(lambda x: '✔️' if x else '❌')
    
    dff["IsBullTrade"] = dff["Last"] > dff["Trade"]
    dff['TradeEmoji'] = dff['IsBullTrade'].apply(lambda x: '✔️' if x else '❌')
    
    dff['MomoEmoji'] = dff['Momo'].apply(lambda x: '✔️' if x == 1.0 else '❌')

    styles = [
        {
            'if': {
                'filter_query': '{GRID} = "Goldilocks"',
                'column_id': 'GRID'
            },
            'backgroundColor': goldilocksColor,
            'color': "white"
        },
        {
            'if': {
                'filter_query': '{GRID} = "Reflation"',
                'column_id': 'GRID'
            },
            'backgroundColor': reflationColor,
            'color': "white"
        },
        {
            'if': {
                'filter_query': '{GRID} = "Inflation"',
                'column_id': 'GRID'
            },
            'backgroundColor': inflationColor,
            'color': "white"
        },
        {
            'if': {
                'filter_query': '{GRID} = "Deflation"',
                'column_id': 'GRID'
            },
            'backgroundColor': deflationColor,
            'color': "white"
        },
        {
            'if': {
                'filter_query': '{PnL} > 0 and {PnL} != 0.0001',
                'column_id': 'PnL'
            },
            'color': greenColor
        },
        {
            'if': {
                'filter_query': '{PnL} < 0 and {PnL} != 0.0001',
                'column_id': 'PnL'
            },
            'color': redColor
        },
        # {
        #     'if': {
        #         'filter_query': '{Chg1D} > 0 and {Chg1D} != 0.0001',
        #         'column_id': 'Chg1D'
        #     },
        #     'color': greenColor,
        #     'fontWeight': 'bold'
        # },
        # {
        #     'if': {
        #         'filter_query': '{Chg1D} < 0 and {Chg1D} != 0.0001',
        #         'column_id': 'Chg1D'
        #     },
        #     'color': redColor,
        #     'fontWeight': 'bold'
        # },
        # {
        #     'if': {
        #         'filter_query': '{Chg1W} > 0 and {Chg1W} != 0.0001',
        #         'column_id': 'Chg1W'
        #     },
        #     'color': greenColor
        # },
        # {
        #     'if': {
        #         'filter_query': '{Chg1W} < 0 and {Chg1W} != 0.0001',
        #         'column_id': 'Chg1W'
        #     },
        #     'color': redColor
        # },
        # {
        #     'if': {
        #         'filter_query': '{Chg1M} > 0 and {Chg1M} != 0.0001',
        #         'column_id': 'Chg1M'
        #     },
        #     'color': greenColor
        # },
        # {
        #     'if': {
        #         'filter_query': '{Chg1M} < 0 and {Chg1M} != 0.0001',
        #         'column_id': 'Chg1M'
        #     },
        #     'color': redColor
        # },
        # {
        #     'if': {
        #         'filter_query': '{Chg3M} > 0 and {Chg3M} != 0.0001',
        #         'column_id': 'Chg3M'
        #     },
        #     'color': greenColor
        # },
        # {
        #     'if': {
        #         'filter_query': '{Chg3M} < 0 and {Chg3M} != 0.0001',
        #         'column_id': 'Chg3M'
        #     },
        #     'color': redColor
        # },
        {
            'if': {'column_id': 'TrendEmoji'},
            'textAlign': 'center'
        },
        {
            'if': {'column_id': 'TradeEmoji'},
            'textAlign': 'center'
        },
        {
            'if': {'column_id': 'MomoEmoji'},
            'textAlign': 'center'
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
        }

    ]

    for col in ['RV', 'RV1D', 'RV1W', 'RV1M']:
        styles.extend(portUtils.get_column_cmap_values(dff, col, -2.0, 2.0, cmap='RdYlGn', reverse=True, low=0, high=0,
                                                       st_threshold_1=1.0, st_threshold_2=-1.0, white_threshold_1=1.0, white_threshold_2=-1.0))
        
    for col in ['Chg1D', 'Chg1W', 'Chg1M', 'Chg3M']:
        styles.extend(portUtils.get_column_cmap_values(dff[dff[col] > 0.0], col, -1.0, 2.0, cmap='Greens', reverse=False, low=0, high=0,
                                                   st_threshold_1=0.0, st_threshold_2=-3.0, white_threshold_1=0.0, white_threshold_2=-4.0,
                                                   data_col=f"{col}_zs", inverse_text_color_rule = False))

    for col in ['Chg1D', 'Chg1W', 'Chg1M', 'Chg3M']:
        styles.extend(portUtils.get_column_cmap_values(dff[dff[col] < 0.0], col, -1.0, 2.0, cmap='Reds', reverse=False, low=0, high=0,
                                                   st_threshold_1=0.0, st_threshold_2=-3.0, white_threshold_1=0.0, white_threshold_2=-4.0,
                                                   data_col=f"{col}_zs", inverse_text_color_rule = False))

    # print(portUtils.get_column_cmap_values(dff, 'BBPos', 0.0, 1.0, cmap='RdYlGn', reverse=False, low=0, high=0,
    #                                                    st_threshold_1=0.25, st_threshold_2=0.75, white_threshold_1=0.25, white_threshold_2=0.75))

    styles.extend(portUtils.get_column_cmap_values(dff, 'BBPos', 0.0, 1.0, cmap='RdYlGn', reverse=False, low=0, high=0,
                                                   st_threshold_1=0.75, st_threshold_2=0.25, white_threshold_1=0.75, white_threshold_2=0.25))

    styles.append({
        'if': {
            'filter_query': '{Ticker} = "Cash"',
            'column_id': ['Last', 'Chg1D', 'Chg1W', 'Chg1M', 'Chg3M', 'PnL', 'RV', 'RV1D', 'RV1W', 'RV1M', 'BBPos', 'TrendEmoji', 'TradeEmoji', 'MomoEmoji']
        },
        'color': 'transparent',
        'backgroundColor': 'transparent'
    })

    assetsDataTable = DataTable(
        id="{}_assets_data_table".format(table_name.replace(" ", "_")),
        data=dff.to_dict("records"),
        columns=columns,
        hidden_columns=['Chg1D_zs', 'Chg1W_zs', 'Chg1M_zs', 'Chg3M', 'Chg3M_zs'],
        css=[{"selector": ".dash-spreadsheet-menu", "rule": "display: none"}],
        sort_action='native',
        style_header=data_table_style_header_dict,
        style_cell=data_table_style_cell_dict,
        style_data_conditional=styles
    )

    return assetsDataTable


def get_portfolio_card(portfolio_name, portfolio):
    card_header_children = []

    if portfolio['total_value'] == portfolio['yday_value']:
        card_header_children.append(f"{portfolio_name}")
    else:
        pct_change = (portfolio['total_value'] / portfolio['yday_value']) - 1.0
        card_header_children.append(html.Span(
            f"{portfolio_name}: {pct_change:+.2%}", className="card-header-font"))
        card_header_children.append(dbc.Button(
            "by Exposure", color="primary", className="float-right", size="lg"))
        card_header_children.append(dbc.Button(
            "by Factor/Sector", color="primary", className="float-right mr-2", size="lg"))
        card_header_children.append(dbc.Button(
            "by Asset Class", color="primary", className="float-right mr-2", size="lg"))

    card = dbc.Card(
        [
            #getCardHeader(f"{portfolio_name}: ${portfolio['total_value']:.2f}", "dark"),
            getCardHeader(card_header_children,
                          "dark" if portfolio['total_value'] == portfolio['yday_value'] else "success" if portfolio['total_value'] >= portfolio['yday_value'] else "danger"),
            dbc.CardBody(
                [
                    html.Div(
                        [get_assets_table(
                            portfolio_name, portfolio['assets'])]
                    )
                ]
            )
        ],
        className="mb-3"
    )

    return card


def get_main_content(portfolios):
    tabs_array = []
    tabs_array.append(dbc.Tab(get_portfolios_tab_content(portfolios), id="portfolio_tab", label="Portfolios"))
    
    # TODO
    # tabs_array.append(dbc.Tab("Sector/Style Factors", id="sector_style_factor_tab", label="Sector/Style Factors"))
    
    tabs_array.extend(get_grid_tabs())
    
    tabs = dbc.Tabs(tabs_array, id="main_tabs")

    return tabs

def get_portfolios_tab_content(portfolios):
    portfolio_cards = []

    portfolio_cards.append(get_portfolio_card(
        'Portfolio', portfolios['Portfolio']))

    for x in portfolios:
        if x != 'Portfolio':
            portfolio_cards.append(get_portfolio_card(x, portfolios[x]))

    return portfolio_cards

def get_grid_tabs():
    return [dbc.Tab(get_grid_tab_content(key, None), id=f"{key}_tab", label=key) for key in rosetta_stone]

def get_grid_tab_content(tab_key, data_store):
    
    table_cards = []
    
    for table in rosetta_stone[tab_key]:
        card = dbc.Card(
            [
                getCardHeader(table['title'], table['outlookClass']),
                dbc.CardBody(
                    [
                        html.Div(tab_key if data_store is None else get_assets_table(f"{tab_key} {table['title']}", data_store["tabData"][tab_key][table['title']], is_portfolio = False))
                    ]
                )
            ],
            className="mb-3"
        )
        
        table_cards.append(card)
    
    return table_cards


def get_asset_modal_contents():
    return
    [
        dbc.ModalHeader("Poop"),
        dbc.ModalBody("Poop"),
    ]

def get_eth_btc_comparison_graph():
    df = dr.getEthBtcCompDf()
    
    df = df[:"2024-12-31"]
    
    layout = {
        "template": "plotly_dark",
        "height": 1000,
        "xaxis_rangeslider_visible": True,
        "margin": {"r": 10, "t": 10, "l": 10, "b": 10},
        "legend": {
            "x": 1.075,
            "y": .95,
        }, 
    }
    
    #fig = dcc.Graph(id="eth-btc-comparison-graph")
    fig = go.Figure(layout=layout)
    
    #print(df)
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["BTC"],
                             mode='lines',
                             line=dict(color='rgba(239, 142, 25, 0.5)', width=2),
                             name='Bitcoin - 03/2013 - Current'))
    
    fig.add_trace(go.Scatter(x=df.index.values, y=df["ETH"],
                             mode='lines',
                             line=dict(color='rgba(165, 252, 246, 1.0)', width=2),
                             name='Ethereum - 06/2017 - Current'))
    
    fig.update_yaxes({
            "title": {"text": "Price", "standoff": 25},
            "side": "right",
            "tickprefix": "     $",
            "tickformat": ',.0f',
            "type": "log",
            "tick0": 1.0,
            "tickvals": [1.0, 3.0, 9.0, 27.0, 81.0, 243.0, 729.0, 2187.0, 6561.0, 19683.0, 59049.0]
        })
    
    return fig

app.layout = html.Div(
    [
        dcc.Interval(id="market-snapshot-interval",
                     interval=60 * 1000, n_intervals=0),
        dcc.Store(id='market-snapshot-store',
                  data=get_assets_data(market_snapshot_assets)),
        dcc.Interval(id="data-interval",
                     interval=3000 * 1000, n_intervals=0),
        dcc.Store(id='data-store',
                  data=portUtils.initializeData()),
        dcc.Store(id='asset-modal-store', data=""),
        dbc.Modal([
            dbc.ModalHeader("Test", id="asset-modal-header", className = "bg-info"),
            dbc.ModalBody(
                dcc.Graph(id="asset-modal-candlestick-graph")
            ),
        ],
            id="asset_modal",
            size="xl",
            is_open=False,
        ),
        dbc.Modal([
            dbc.ModalHeader("ETH - BTC Comparison", id="eth-btc-comparison-modal-header", className = "bg-warning"),
            dbc.ModalBody(
                dcc.Graph(id="eth-btc-comparison-graph", figure = get_eth_btc_comparison_graph())
                
            ),
        ],
            id="eth-btc-comparison-modal",
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
                                        html.H4("The Macro™ Dashboard®"),
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
                        side_bar,
                        xs=2,
                        className="dbc_dark"
                    ),
                        dbc.Col([dbc.Alert("Click the table", id='out', className="pb-3", is_open = False), get_main_content(empty_data["portfolios"])],
                        xs=10,
                        id="main_content"
                    )],
                    className="dbc_dark mt-4"
                )
            ])]
)

chartSolidGreen = "#3D9970"
chartTransGreen = 'rgba(61,153,112,0.1)'
chartSolidRed = "#FF4136"
chartTransRed = 'rgba(255,65,54,0.1)'


def fillBridgeBand(bullTrend):
    if bullTrend is None:
        return chartTransGreen
    else:
        return chartTransRed


def addUpVolume(fig, df, name, enumValue):
    volume = df.loc[(df["close"] > df["close"].shift(1)) & (df["VolumeEnum"] == enumValue)]
    
    volume_colors = portUtils.get_cmap_value(volume["VolumeEnum"], -1, 3, 'Greens', False)
    
    fig.add_trace(go.Bar(x=volume.index.values, y=volume["volume"],
                showlegend=True,
                name=name,
                legendgroup="Volume",
                marker=dict(color= volume_colors)),
        row=2, col=1)
    
def addDownVolume(fig, df, name, enumValue):
    volume = df.loc[(df["close"] < df["close"].shift(1)) & (df["VolumeEnum"] == enumValue)]
    
    volume_colors = portUtils.get_cmap_value(volume["VolumeEnum"], -3, 1, 'Reds', True)
    
    fig.add_trace(go.Bar(x=volume.index.values, y=volume["volume"],
                showlegend=True,
                name=name,
                legendgroup="Volume",
                marker=dict(color= volume_colors)),
        row=2, col=1)

def get_eth_btc_comparison_graph():
    layout = {
        "template": "plotly_dark",
        "xaxis_rangeslider_visible": True,
        "margin": {"r": 10, "t": 10, "l": 10, "b": 10},
        "legend": {
            "x": 1.075,
            "y": .95,
        }, 
    }
    
    #fig = dcc.Graph(id="eth-btc-comparison-graph")
    fig = go.Figure(id="eth-btc-comparison-graph", layout=layout)
    
    return fig

@app.callback([Output('asset-modal-candlestick-graph', 'figure'), Output("asset-modal-header", "children")],
              Input('asset-modal-store', 'data'))
def update_asset_modal_candlestick_graph(ticker):
    if ticker == "":
        return go.Figure(), ""
    
    df = portUtils.get_data_for_ticker(ticker, 180)

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

    df["BullTrend"] = df["Trend"]
    df.loc[(df['Trend'] > df['close']), 'BullTrend'] = None

    df["BearTrend"] = df["Trend"]
    df.loc[(df['Trend'] < df['close']), 'BearTrend'] = None

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
    
    df["BullTrade"] = df["Trade"]
    df.loc[(df['Trade'] > df['close']), 'BullTrade'] = None

    df["BearTrade"] = df["Trade"]
    df.loc[(df['Trade'] < df['close']), 'BearTrade'] = None
    
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

    fig.add_trace(go.Candlestick(
        x=df.index.values,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        showlegend=False,
    ), row=1, col=1)


    ################Volume###############

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
    
    # weakUpVolume = df.loc[(df["close"] > df["close"].shift(1)) & (df["VolumeEnum"] == 0.0)]
    
    # weakUpVolume_colors = portUtils.get_cmap_value(weakUpVolume["VolumeEnum"], -1, 3, 'Greens', False)
    
    # fig.add_trace(go.Bar(x=weakUpVolume.index.values, y=weakUpVolume["volume"],
    #                       showlegend=True,
    #                       name="Weak",
    #                       legendgroup="Volume",
    #                       marker=dict(color= weakUpVolume_colors)),
    #               row=2, col=1)
    
    # downVolume = df.loc[df["close"] < df["open"]]
    
    # downVolume_colors = portUtils.get_cmap_value(downVolume["VolumeEnum"], -3, 1, 'Reds', True)
    
    # fig.add_trace(go.Bar(x=downVolume.index.values, y=downVolume["volume"],
    #                       showlegend=False,
    #                       marker=dict(color= downVolume_colors)),
    #               row=2, col=1)
    
    fig.update_xaxes({"showgrid": True}, row=2, col=1)
    
    fig.update_yaxes({
            "title": {"text": "Volume", "standoff": 25},
            "side": "right",
            "tickprefix": "     ",
            "type": "log"
        }, row=2, col=1)
    
    ################Volatility###############
    fig.add_trace(go.Bar(x=df.index.values, y=df["RV"],
                          showlegend=False,
                          marker=dict(color= [ portUtils.get_single_cmap_value([rv], -2, 2, cmap='RdYlGn', reverse=True)[0] for rv in df["RV"]])),
                  row=3, col=1)

    fig.update_xaxes({"showgrid": True}, row=3, col=1)

    fig.update_yaxes({
            "title": {"text": "RVol", "standoff": 25},
            "tickformat": ".0f",
            "side": "right",
            "tickprefix": "     ",
            "tick0": 0.0,
            "dtick": 1.0,
            "range": [-3.1, 3.1]
        }, row=3, col=1)
    
    
     # "title":{
     #        'y':0.9,
     #        'x':0.1,
     #        'xanchor': 'left',
     #        'yanchor': 'top'}
    
    fig.layout.annotations[0].update(x=0.065)
    fig.layout.annotations[0].update(y=0.9875)
    fig.layout.annotations[1].update(x=0.025)
    fig.layout.annotations[2].update(x=0.025)
    
    fig.update_layout(height=1000)
    
    #fig.update_yaxes(range=[3, 9])

    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]),  # hide weekends
        ]
    )

    # fig.update_yaxes(title_text='Price')

    # fig.update_layout(
    #     xaxis_rangeslider_visible=False,
    #     margin={"r":10,"t":10,"l":10,"b":10}
    # )

    return fig, f"{ticker} - Chart and Technicals"


@app.callback(Output("market-snapshot-timestamp", "children"), [Input("market-snapshot-interval", "n_intervals")])
def update_market_snapshot_timestamp(n):
    return "*updated at {} (delayed 15 min)".format(datetime.datetime.now().strftime("%#I:%M %p"))


@app.callback(
    Output("market-snapshot-store", "data"),
    [Input("market-snapshot-interval", "n_intervals")],
    [State("market-snapshot-store", "data")])
def update_market_snapshot_store(n, previous_data):
    previous_data_df = pd.read_json(previous_data, orient='split')

    data = previous_data_df.copy()

    # data[["Last", "Change", "Previous"]] = data[[
    #     "Last", "Change", "Previous"]].apply(pd.to_numeric)

    endDate = datetime.date.today() + datetime.timedelta(days=1)
    startDate = (endDate - datetime.timedelta(days=10))

    for ticker in data.index.values:
        if ticker == "Blank":
            data.at[ticker, "Last"] = .01
            data.at[ticker, "Change"] = .01
            data.at[ticker, "Previous"] = .01
        else:
            hist = dr.DownloadYahooData(ticker, startDate, endDate)

            previous = data.at[ticker, "Last"]
            p1 = hist.at[hist.index.values[-1], 'close']
            p2 = hist.at[hist.index.values[-2], 'close']

            data.at[ticker, "Last"] = p1
            data.at[ticker, "Change"] = ((p1-p2)/p2)
            data.at[ticker, "Previous"] = previous

    return data.to_json(date_format='iso', orient='split')


@app.callback(Output('market_snapshot_data_table', 'data'), Input('market-snapshot-store', 'data'))
def update_market_snapshot_data_table(jsonified_big_board_data):
    dff = pd.read_json(jsonified_big_board_data, orient='split')

    # quote_rows = []

    # for ticker in dff.index.values:
    #     print(ticker)
    #     quote_rows.append(html.Div(
    #         className="rows",
    #         children=[
    #             html.P(
    #                 ticker,
    #                 className="three-col")
    #         ])
    #     )

    return dff.to_dict("records")


@app.callback(
    Output("data-store", "data"),
    [Input("data-interval", "n_intervals")],
    [State("data-store", "data")])
def update_data_store(n, previous_data):
    # TODO
    portUtils.update_asset_dfs(previous_data)
    updated_data = portUtils.updateAssetTables(previous_data)
    
    return previous_data
    #return updated_data


@app.callback(Output('portfolio_tab', 'children'), Input('data-store', 'data'))
def update_portfolios_content(data):

    return get_portfolios_tab_content(data["portfolios"])


@app.callback(Output('Goldilocks_tab', 'children'), Input('data-store', 'data'))
def update_goldilocks_tab_content(data_store):
    return get_grid_tab_content("Goldilocks", data_store)

@app.callback(Output('Reflation_tab', 'children'), Input('data-store', 'data'))
def update_reflation_tab_content(data_store):
    return get_grid_tab_content("Reflation", data_store)

@app.callback(Output('Inflation_tab', 'children'), Input('data-store', 'data'))
def update_inflation_tab_content(data_store):
    return get_grid_tab_content("Inflation", data_store)

@app.callback(Output('Deflation_tab', 'children'), Input('data-store', 'data'))
def update_deflation_tab_content(data_store):
    return get_grid_tab_content("Deflation", data_store)

# , Output('asset_modal', 'is_open')

#    return [dbc.Tab(get_grid_tab_content(key, None), id=f"{key}_tab", label=key) for key in rosetta_stone]

# def get_grid_tab_content(tab_key, data_store):

asset_tables_inputs = []
for key in empty_data["portfolios"]:
    asset_tables_inputs.append(
        Input("{}_assets_data_table".format(key.replace(" ", "_")), 'active_cell'))



@app.callback(
    [Output('out', 'children'), Output('asset_modal', 'is_open'),
     Output('asset-modal-store', 'data')],
    asset_tables_inputs,
    [State("data-store", "data")])
def update_graphs(active_cell_1, active_cell_2, active_cell_3, data_store):
    ctx = dash.callback_context

    control_id = ""

    if not ctx.triggered:
        control_id = ", ".join(list(data_store["portfolios"].keys()))
    else:
        control_id = ctx.triggered[0]['prop_id'].split(
            '.')[0].replace("_assets_data_table", "").replace("_", " ")


    active_cell = None
    active_ticker = ""

    if active_cell_1 and control_id == "401k Portfolio":
        active_cell = active_cell_1
        active_ticker = active_cell['row_id']
    elif active_cell_2 and control_id == "Roth Portfolio":
        active_cell = active_cell_2
        active_ticker = active_cell['row_id']
    elif active_cell_3 and control_id == "Portfolio":
        active_cell = active_cell_3
        active_ticker = active_cell['row_id']

    return control_id, True if active_cell is not None else False, active_ticker

@app.callback(
    Output("eth-btc-comparison-modal", "is_open"),
    Input("open-eth-btc-comparison-modal", "n_clicks"),
    State("eth-btc-comparison-modal", "is_open"),
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(debug=True, port='1203')
