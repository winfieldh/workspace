from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross


class SMACrossOver(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod, initialCash):
        strategy.BacktestingStrategy.__init__(self, feed, initialCash)
        self.__instrument = instrument
        self.__position = None
        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(True)
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__sma = ma.SMA(self.__prices, smaPeriod)

    def getSMA(self):
        return self.__sma

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if cross.cross_above(self.__prices, self.__sma) > 0:
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                # Enter a buy market order. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, shares, True)
                self.info("Entering position...%s on %s. Shares: %d" % (self.getLastPrice(self.__instrument),self.getCurrentDateTime(),shares))
        # Check if we have to exit the position.
        elif not self.__position.exitActive() and (cross.cross_below(self.__prices, self.__sma) > 0):
            self.__position.exitMarket()
            myDays = self.__position.getAge().days
            myReturn = self.__position.getReturn(includeCommissions=False)
            self.info("exiting position...%s on %s. Shares: %d. Age: %s Return: %s" % (self.getLastPrice(self.__instrument),self.getCurrentDateTime(),self.getBroker().getShares(self.__instrument),myDays,myReturn))