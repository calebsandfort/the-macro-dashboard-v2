# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 16:21:48 2021

@author: csandfort
"""
import datetime
import dataRetrieval as dr 

startDate = datetime.datetime.strptime('2019-01-01', '%Y-%m-%d')
endDate = datetime.datetime.today()

ftMacroTickers = ['XLY', 'XLF', 'XLK', 'XLB', 'XLI', 'XLE', 'XLRE', 'XLP', 'XLU', 'XLC']
#ftMacroTickers = ['XLY']

#dr.GetTdaDataForTickers(ftMacroTickers, 'month', 'daily', 1, startDate, endDate, False, True)

# for ticker in ftMacroTickers:
#     tda_daily_data = dr.GetTdaData(ticker, 'month', 'daily', 1, startDate, endDate, False, True)