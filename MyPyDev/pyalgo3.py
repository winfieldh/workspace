#!/usr/bin/python

from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        strategy.BacktestingStrategy.__init__(self, feed)
        # We want a 15 period SMA over the closing prices.
        self.__sma = ma.SMA(feed[instrument].getCloseDataSeries(), 15)
        self.__instrument = instrument

    def onBars(self, bars):
        bar = bars[self.__instrument]
        self.info("%s %s" % (bar.getClose(), self.__sma[-1]))
instrument = "spy"
# Load the yahoo feed from the CSV file
feed = yahoofeed.Feed()
feed.addBarsFromCSV(instrument, instrument+".csv")

# Evaluate the strategy with the feed's bars.
myStrategy = MyStrategy(feed, instrument)
myStrategy.run()