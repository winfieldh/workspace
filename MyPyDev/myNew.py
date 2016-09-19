from pyalgotrade import plotter
from pyalgotrade.tools import yahoofinance
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import rsi
from pyalgotrade.technical import cross
from pyalgotrade.technical import stoch

class RSI2A(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, entrySMA, exitSMA, rsiPeriod, overBoughtThreshold, overSoldThreshold):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        # We'll use adjusted close values, if available, instead of regular close values.
        if feed.barsHaveAdjClose():
            self.setUseAdjustedValues(True)
        self.__priceDS = feed[instrument].getPriceDataSeries()
        self.__entrySMA = ma.SMA(self.__priceDS, entrySMA)
        self.__exitSMA = ma.SMA(self.__priceDS, exitSMA)
        self.__fastSMA = ma.SMA(self.__priceDS, 20)
        self.__slowSMA = ma.SMA(self.__priceDS, 100)
        self.__rsi = rsi.RSI(self.__priceDS, rsiPeriod)
  #      self.__stochD = stoch.StochasticOscillator(self.__priceDS,meth)
        self.__overBoughtThreshold = overBoughtThreshold
        self.__overSoldThreshold = overSoldThreshold
        self.__longPos = None
        self.__shortPos = None

        self.__barDs = self.getFeed()[self.__instrument]
        self.__stochK = stoch.StochasticOscillator(self.__barDs,30,24)
        self.__stochK = stoch.StochasticOscillator.getD(self.__stochK)
        self.__stochD = ma.SMA(self.__stochK, 11)
        
        
    def getEntrySMA(self):
        return self.__entrySMA

    def getExitSMA(self):
        return self.__exitSMA

    def getRSI(self):
        return self.__rsi

    def onEnterCanceled(self, position):
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)

    def onExitOk(self, position):
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate SMA and RSI.
#         if self.__exitSMA[-1] is None or self.__entrySMA[-1] is None or self.__rsi[-1] is None:
#             return

        bar = bars[self.__instrument]
        if self.__longPos is not None: #we have a long
            #if self.exitLongSignal(): #check if we should exit
            if (self.__longPos.getAge().days > 60) or (self.__longPos.getReturn() > .05):
                self.info("Exiting %s. Held for %s. Date: %s. Return: %0.2f" % (self.__instrument, self.__longPos.getAge().days,self.getCurrentDateTime(),self.__longPos.getReturn()))
                self.info("Stoch: %s" % (self.__stochK[-1]))
                self.__longPos.exitMarket() # exit long position
                
        elif self.__shortPos is not None: #we have a short
            if self.exitShortSignal(): #check if we should exit short
                self.__shortPos.exitMarket() # exit short position
        else: # we have no position so check to enter
            if self.enterLongSignal(bar):
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                self.__longPos = self.enterLong(self.__instrument, shares, True)
                self.info("Entering %s. Date: %s" % (self.__instrument, self.getCurrentDateTime()))

            elif self.enterShortSignal(bar):
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                self.__shortPos = self.enterShort(self.__instrument, shares, True)

    def enterLongSignal(self, bar):
        return self.__stochK[-3] < 50 and self.__stochK[-2] > 50
#        return cross.cross_above(self.__fastSMA,self.__slowSMA,-2)
        #return self.__longPos.getAge().days > 20

    def exitLongSignal(self):
        return self.__rsi[-2] <= 50 and self.__rsi[-1] > 50

    def enterShortSignal(self, bar):
        return self.__rsi[-1] >= self.__overBoughtThreshold

    def exitShortSignal(self):
        return cross.cross_below(self.__priceDS, self.__exitSMA)


def main(plot):
    instrument = "DIA"
    entrySMA = 200
    exitSMA = 5
    rsiPeriod = 7
    overBoughtThreshold = 90
    overSoldThreshold = 30

    # Download the bars.
    feed = yahoofinance.build_feed([instrument], 2012, 2016, ".")

    strat = RSI2A(feed, instrument, entrySMA, exitSMA, rsiPeriod, overBoughtThreshold, overSoldThreshold)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)

    if plot:
        plt = plotter.StrategyPlotter(strat, True, False, True)
        plt.getInstrumentSubplot(instrument).addDataSeries("Entry SMA", strat.getEntrySMA())
        plt.getInstrumentSubplot(instrument).addDataSeries("Exit SMA", strat.getExitSMA())
        plt.getOrCreateSubplot("rsi").addDataSeries("RSI", strat.getRSI())
        plt.getOrCreateSubplot("rsi").addLine("Overbought", overBoughtThreshold)
        plt.getOrCreateSubplot("rsi").addLine("Oversold", overSoldThreshold)

    strat.run()
    print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05)

    if plot:
        plt.plot()


if __name__ == "__main__":
    main(True)