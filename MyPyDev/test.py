from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
from pyalgotrade.tools import yahoofinance
from pyalgotrade.technical import stoch

class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        super(MyStrategy, self).__init__(feed)
        # We want a 15 period SMA over the closing prices.
        self.__instrument = instrument
        self.__sma = ma.SMA(feed[instrument].getCloseDataSeries(), 15)
        self.__barDs = self.getFeed()[self.__instrument]
        self.__stochK = stoch.StochasticOscillator(self.__barDs,30,24)
        self.__stochK = stoch.StochasticOscillator.getD(self.__stochK)
        self.__stochD = ma.SMA(self.__stochK, 11)
        
    def onBars(self, bars):
        bar = bars[self.__instrument]
        if (self.__stochD[-1] is not None):
            self.info("%s %s %s %s" % (bar.getClose(), self.__sma[-1], self.__stochK[-5], self.__stochD[-1]))

# Load the yahoo feed from the CSV file
yahoofinance.download_daily_bars('ibm', 2016, 'ibm-2016.csv')
feed = yahoofeed.Feed()
feed.addBarsFromCSV("ibm", "ibm-2016.csv")

# Evaluate the strategy with the feed's bars.
myStrategy = MyStrategy(feed, "ibm")
myStrategy.run()