# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 16:09:12 2022

@author: csandfort
"""
import nasdaqdatalink

nasdaqdatalink.ApiConfig.api_key = 'Y9Lf787ZrM5gcGKv-6W7'
test = nasdaqdatalink.get('OPT/MSFT', start_date='2018-12-31', end_date='2018-12-31')
idx = test.index.values[0]

m2atmiv = test.at[idx, "m2atmiv"]

slope = test.at[idx, "slope"]

deriv = test.at[idx, "deriv"]

slopeInf = test.at[idx, "slope_inf"]

derivInf = test.at[idx, "deriv_inf"]

delta = .25

slope = 0.71 * slope + 0.29 * slopeInf

deriv = 0.71 * deriv + 0.29 * derivInf

iv_25 = m2atmiv * (1 + (slope/1000 + (deriv/1000 * (delta*100-50)/2) )* (delta*100-50))

delta = .5

iv_50 = m2atmiv * (1 + (slope/1000 + (deriv/1000 * (delta*100-50)/2) )* (delta*100-50))


delta = .75

iv_75 = m2atmiv * (1 + (slope/1000 + (deriv/1000 * (delta*100-50)/2) )* (delta*100-50))