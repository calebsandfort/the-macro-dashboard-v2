# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 11:42:25 2022

@author: csandfort
"""
import pandas as pd
from os.path import exists
import math
import dataRetrieval as dr
import datetime
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-t", "--ticker", help="ticker", required=True)

parser.add_argument("-ml", "--max_loss", help="max_loss", type=float, required=True)

parser.add_argument("-d", "--direction", help="Direction", required=True)

args = parser.parse_args()

startDate = datetime.datetime.strptime('2016-05-01', '%Y-%m-%d')
endDate = datetime.datetime.today()

data = dr.GetTdaDataForTickers([args.ticker], 'month', 'daily', 1, startDate, endDate, False, True)

original_df = data[args.ticker]
original_df.drop('high', inplace=True, axis = 1)
original_df.drop('low', inplace=True, axis = 1)
original_df.drop('open', inplace=True, axis = 1)
original_df.drop('volume', inplace=True, axis = 1)

original_index_values = original_df.index.values
original_closes = original_df["close"].values


r = list(range(-1, (-20 * 36) - 1, -20))

new_index_values = []
new_closes = []
pct_chgs = []

for i in r:
    new_index_values.insert(0, original_index_values[i])
    new_closes.insert(0, original_closes[i])

for i in range(0, len(new_closes) - 1):
    pct_chgs.append((new_closes[i + 1] - new_closes[i])/new_closes[i])

mean = sum(pct_chgs) / len(pct_chgs)
variance = sum([((x - mean) ** 2) for x in pct_chgs]) / len(pct_chgs)
monthly_vol = variance ** 0.5

close = original_closes[-1]

portfolio_value = 180000
stop_loss_sigma = 1.5
stop_loss_offset = close * stop_loss_sigma * monthly_vol
stop_loss_percent = args.max_loss / 100.0
stop_loss_notional_value = portfolio_value * stop_loss_percent

profit_target_sigma = 2.25
profit_target_offset = close * profit_target_sigma * monthly_vol

shares = math.floor(stop_loss_notional_value / stop_loss_offset)
notional_value = shares * close
profit_target_gain = profit_target_offset * shares / portfolio_value

long_stop_loss_value = close - stop_loss_offset
long_profit_target_value = close + profit_target_offset

short_stop_loss_value = close + stop_loss_offset
short_profit_target_value = close - profit_target_offset

print()
print()
print()
print()

print(f"{args.ticker} Monthly Vol: {monthly_vol:.2%}")
print(f"Max Loss: {stop_loss_percent:.2%}")
print(f"Target Gain: {profit_target_gain:.2%}")
print()

print(f"Current Price: ${close:,.2f}")
print(f"Shares: {shares}")
print(f"Notional Value: ${notional_value:,.2f}")
print()

if args.direction == "long":
    print(f"Long Stop: ${long_stop_loss_value:,.2f}")
    print(f"Long Target: ${long_profit_target_value:,.2f}")

if args.direction == "short":
    print(f"Short Stop: ${short_stop_loss_value:,.2f}")
    print(f"Short Target: ${short_profit_target_value:,.2f}")
    
    
    