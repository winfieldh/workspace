from pyalgotrade import strategy
from pyalgotrade import plotter
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
from pyalgotrade.technical import cumret
from pyalgotrade.technical import roc
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import trades
from pyalgotrade.technical import rsi
import os
from datetime import date

class MarketTiming(strategy.BacktestingStrategy):
    def __init__(self, feed, instruments, initialCash, myroc):
        strategy.BacktestingStrategy.__init__(self, feed, initialCash )
        self.setUseAdjustedValues(True)
        self.__instruments = instruments
        self.__rebalanceMonth = None
        self.__sharesToBuy = {}
        # Initialize indicators for each instrument.
        self.__sma = {}
        self.__sma2 = {}
        self.__sma3 = {}
        self.__roc = {}
        self.__rsi = {}
        
        for instrument in instruments:
            priceDS = feed[instrument].getPriceDataSeries()
            self.__sma[instrument] = ma.SMA(priceDS, 200)
            self.__roc[instrument] = roc.RateOfChange(priceDS, myroc)
            self.__rsi[instrument] = rsi.RSI(priceDS, 14)
            
        #Initialize 2nd sma for VFINX
        priceDS = feed["VFINX"].getPriceDataSeries()
        self.__sma2["VFINX"] = ma.SMA(priceDS,50)
        self.__sma3["VFINX"] = ma.SMA(priceDS,200)

    def _shouldRebalance(self, dateTime):
#         return (dateTime.month != self.__rebalanceMonth)
        return (dateTime.weekday() == 4)
    
    def _getRank(self, instrument):
        # If the price is below the SMA, then this instrument doesn't rank at
        # all.
        smas = self.__sma[instrument]
        price = self.getLastPrice(instrument)
        rsi = self.__rsi[instrument]
#         self.info("Here is roc  %0.4f " % self.__roc[instrument][-1])
        rocs = self.__roc[instrument]
        # or self.__roc[instrument][-1] < 0 or price < smas[-1] len(smas) == 0 or smas[-1] is None or self.__roc[instrument][-1] < 0
        if  price < smas[-1] or rocs[-1]*1000 < 40:
            ret = 0
        else:
            ret = 1
        return ret

#     def _getTopInstruments(self, instrument):
#         # Find the instrument with the highest rank.
#         ret = None
#         highestRank = None
#         for instrument in self.__instrumentsByClass[assetClass]:
#             rank = self._getRank(instrument)
#             if rank is not None and (highestRank is None or rank > highestRank):
#                 highestRank = rank
#                 ret = instrument
#         return ret

    def _getTop(self):
        topInstruments = []
        for instrument in self.__instruments:
            rank = self._getRank(instrument)
            if rank == 1:
                topInstruments.append(instrument)            
        return topInstruments

    def _placePendingOrders(self):
        remainingCash = self.getBroker().getCash() * 0.9 # Use less chash just in case price changes too much.
        for instrument in self.__sharesToBuy:
            orderSize = self.__sharesToBuy[instrument]
            if orderSize > 0:
                # Adjust the order size based on available cash.
                lastPrice = self.getLastPrice(instrument)
                cost = orderSize * lastPrice
                while cost > remainingCash and orderSize > 0:
                    orderSize -= 1
                    cost = orderSize * lastPrice
                if orderSize > 0:
                    remainingCash -= cost
                    assert(remainingCash >= 0)

            if orderSize != 0:
                print ("Placing market order for %s %s shares" % (orderSize, instrument))
                self.marketOrder(instrument, orderSize, goodTillCanceled=True)
                self.__sharesToBuy[instrument] -= orderSize
                
    def _logPosSize(self):
        totalEquity = self.getBroker().getEquity()
        positions = self.getBroker().getPositions()
        for instrument in self.getBroker().getPositions():
            posSize = positions[instrument] * self.getLastPrice(instrument) / totalEquity * 100
#             posAge = positions[instrument].getAge()
            self.info("%s - %0.2f %%" % (instrument, posSize))

    def _rebalance(self):
        self.info("Rebalancing")
#         self._logPosSize()
        smashort = self.__sma2["VFINX"]
        smalong = self.__sma3["VFINX"]
#         if 1:
#         self.info("smashort %5.4f smalong %5.4f" % (smashort[-1],smalong[-1]))
        if smashort[-1] > smalong[-1] and smalong[-1] is not None:
                # Cancel all active/pending orders.
            for order in self.getBroker().getActiveOrders():
                self.getBroker().cancelOrder(order)
            cashPerInstrument = self.getBroker().getEquity() / float(5) #20 is number of positions
            self.__sharesToBuy = {}
    
            # Calculate which positions should be open during the next period.
            topInstruments = self._getTop()
            for instrument in topInstruments:                    
#                 print("%s ... Best for class %s: %s" % (myTimestamp, assetClass, instrument))
#                 print ("Best for class %s: %s" % (assetClass, instrument))
                self.info("To Buy %s" % topInstruments)
                if instrument is not None:
                    lastPrice = self.getLastPrice(instrument)
                    cashForInstrument = cashPerInstrument - self.getBroker().getShares(instrument) * lastPrice
                    # This may yield a negative value and we have to reduce this
                    # position.
                    self.__sharesToBuy[instrument] = int(cashForInstrument / lastPrice)
    
            # Calculate which positions should be closed.
            for instrument in self.getBroker().getPositions():
                if instrument not in topInstruments:
                    currentShares = self.getBroker().getShares(instrument)
                    assert(instrument not in self.__sharesToBuy)
                    self.__sharesToBuy[instrument] = currentShares * -1
        else:
            for instrument in self.getBroker().getPositions():
                currentShares = self.getBroker().getShares(instrument)
#                assert(instrument not in self.__sharesToBuy)
                self.__sharesToBuy[instrument] = currentShares * -1
                
    def getAcctValue(self):
        acctValue = self.getBroker().getEquity()
        self.info ("Account Value = %.2f" % acctValue)
        
    def onBars(self, bars):
        currentDateTime = bars.getDateTime()
        if self._shouldRebalance(currentDateTime):
            self.__rebalanceMonth = currentDateTime.month
            self._rebalance()
            
        self._placePendingOrders()
       

def main(plot):
    for x in range(10,20,10):
        riskFreeRate = 0.02
        initialCash = 100000
        myroc = x
        print x
        beginYear = 2000
        endYear = date.today().year
        feed = yahoofeed.Feed()
        instruments = ("VFINX","AXP","BA","CAT","CSCO","CVX","DD","DIS","GE","GS","HD","IBM","INTC","JNJ","JPM","KO","MCD","MMM","MRK","MSFT","NKE","PFE","PG","T","TRV","UNH","UTX","VZ","WMT","XOM")
#        # Download the bars.
        for instrument in instruments:
            for year in range(beginYear,endYear+1,1):
                filename = "data/%s-%d-yahoofinance.csv" % (instrument,year)
                if os.path.isfile(filename):
                    feed.addBarsFromCSV(instrument,filename)

   
        strat = MarketTiming(feed, instruments, initialCash, myroc)
        returnsAnalyzer = returns.Returns()
        strat.attachAnalyzer(returnsAnalyzer)
        sharpeRatioAnalyzer = sharpe.SharpeRatio()
        strat.attachAnalyzer(sharpeRatioAnalyzer)
        drawDownAnalyzer = drawdown.DrawDown()
        strat.attachAnalyzer(drawDownAnalyzer)
        tradesAnalyzer = trades.Trades()
        strat.attachAnalyzer(tradesAnalyzer)
        if plot:
            plt = plotter.StrategyPlotter(strat, False, False, True)
            plt.getOrCreateSubplot("cash").addCallback("Cash", lambda x: strat.getBroker().getCash())
            # Plot strategy vs. SPY cumulative returns.
#             plt.getOrCreateSubplot("returns").addDataSeries("VFINX", cumret.CumulativeReturn(feed["VFINX"].getPriceDataSeries()))
#             plt.getOrCreateSubplot("returns").addDataSeries("Strategy", returnsAnalyzer.getCumulativeReturns())
#        
        strat.run()
        #print LBPs, (returnsAnalyzer.getCumulativeReturns()[-1] * 100)/float(12)
        if (returnsAnalyzer.getCumulativeReturns()[-1] * 100)/float((endYear-1)-beginYear) > 0:
            print
            print "Final portfolio value: $%.2f" % strat.getResult()
            print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(riskFreeRate)
            print "Cumulative Returns: %.2f %%" % (returnsAnalyzer.getCumulativeReturns()[-1] * 100)
            AvgAnnRet = (returnsAnalyzer.getCumulativeReturns()[-1] * 100)/float((endYear-1)-beginYear)
            print "Average Annual Returns: %.2f %%" % AvgAnnRet
            print "Max. drawdown: %.2f %%" % (drawDownAnalyzer.getMaxDrawDown() * 100)
            print "Longest drawdown duration: %s" % (drawDownAnalyzer.getLongestDrawDownDuration())
            print
            print "Total trades: %d" % (tradesAnalyzer.getCount())
            if tradesAnalyzer.getCount() > 0:
                profits = tradesAnalyzer.getAll()
                print "Avg. profit: $%2.f" % (profits.mean())
                print "Profits std. dev.: $%2.f" % (profits.std())
                print "Max. profit: $%2.f" % (profits.max())
                print "Min. profit: $%2.f" % (profits.min())
                returns1 = tradesAnalyzer.getAllReturns()
                print "Avg. return: %2.f %%" % (returns1.mean() * 100)
                print "Returns std. dev.: %2.f %%" % (returns1.std() * 100)
                print "Max. return: %2.f %%" % (returns1.max() * 100)
                print "Min. return: %2.f %%" % (returns1.min() * 100)
#                 for x in returns1:
#                     print x * 100
#             print
#             print "Profitable trades: %d" % (tradesAnalyzer.getProfitableCount())
#             if tradesAnalyzer.getProfitableCount() > 0:
#                 profits = tradesAnalyzer.getProfits()
#                 print "Avg. profit: $%2.f" % (profits.mean())
#                 print "Profits std. dev.: $%2.f" % (profits.std())
#                 print "Max. profit: $%2.f" % (profits.max())
#                 print "Min. profit: $%2.f" % (profits.min())
#                 returns1 = tradesAnalyzer.getPositiveReturns()
#                 print "Avg. return: %2.f %%" % (returns1.mean() * 100)
#                 print "Returns std. dev.: %2.f %%" % (returns1.std() * 100)
#                 print "Max. return: %2.f %%" % (returns1.max() * 100)
#                 print "Min. return: %2.f %%" % (returns1.min() * 100)
#                 
# 
#             print
#             print "Unprofitable trades: %d" % (tradesAnalyzer.getUnprofitableCount())
#             if tradesAnalyzer.getUnprofitableCount() > 0:
#                 losses = tradesAnalyzer.getLosses()
#                 print "Avg. loss: $%2.f" % (losses.mean())
#                 print "Losses std. dev.: $%2.f" % (losses.std())
#                 print "Max. loss: $%2.f" % (losses.min())
#                 print "Min. loss: $%2.f" % (losses.max())
#                 returns1 = tradesAnalyzer.getNegativeReturns()
#                 print "Avg. return: %2.f %%" % (returns1.mean() * 100)
#                 print "Returns std. dev.: %2.f %%" % (returns1.std() * 100)
#                 print "Max. return: %2.f %%" % (returns1.max() * 100)
#                 print "Min. return: %2.f %%" % (returns1.min() * 100)

        if plot:
            plt.plot()
#             
            
if __name__ == "__main__":
    main(True)