#!/usr/bin/python

from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.tools import yahoofinance

class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument

    def onBars(self, bars):
        bar = bars[self.__instrument]
        self.info(bar.getClose())

instrument = "spy"
# Load the yahoo feed from the CSV file
feed = yahoofinance.build_feed([instrument], 2014, 2014, "data")

# Evaluate the strategy with the feed's bars.
myStrategy = MyStrategy(feed, instrument)
myStrategy.run()
