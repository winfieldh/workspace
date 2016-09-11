#!/usr/bin/python
from pyalgotrade import bar
from pyalgotrade.tools import yahoofinance
##yahoofinance.download_daily_bars('orcl', 2000, 'orcl-2000.csv')
instrument = "yhoo"
feed = yahoofinance.build_feed([instrument], 2011, 2012, "./data")