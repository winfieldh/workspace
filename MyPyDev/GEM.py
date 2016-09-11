#!/usr/bin/python

from pyalgotrade import strategy
from pyalgotrade import plotter
from pyalgotrade.technical import ma
from pyalgotrade.technical import cumret
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import trades
import os
from datetime import date
from pyalgotrade.barfeed import yahoofeed

class MarketTiming(strategy.BacktestingStrategy):
    def __init__(self, feed, instruments, initialCash, LBPs):
        strategy.BacktestingStrategy.__init__(self, feed, initialCash)
        if feed.barsHaveAdjClose():
            self.setUseAdjustedValues(True)
        self.__instruments = instruments
        self.__rebalanceMonth = None
        self.__sharesToBuy = {}
        # Initialize indicators for each instrument.
        self.__sma = {}
        self.__LBPs = LBPs

    def _shouldRebalance(self, dateTime):
        return dateTime.month != self.__rebalanceMonth
#         return (dateTime.weekday() == 4)
       
    def _getRank(self, instrument):
        # If the price is below the SMA, then this instrument doesn't rank at
        # all.
#         smas = self.__sma[instrument]
#         price = self.getLastPrice(instrument)
#         if len(smas) == 0 or smas[-1] is None or price < smas[-1]:
#             return None

        # Rank based on 20 day returns.
        ret = 0
        lookBackPeriods = self.__LBPs
        for i in lookBackPeriods:
            lookBack = i
            priceDS = self.getFeed()[instrument].getPriceDataSeries()
            if len(priceDS) >= lookBack:
                ret += (priceDS[-1] - priceDS[-1*lookBack]) / float(priceDS[-1*lookBack])
        retavg = ret / float((len(lookBackPeriods)))
        return retavg

    def _getBestOf2(self, instrument1, instrument2):
        # Find the instrument with the highest rank.
        ret = None
        rank1 = self._getRank(instrument1)
        rank2 = self._getRank(instrument2)
        if rank1 > rank2:
            ret = instrument1
        else:
            ret = instrument2
        return ret

    def _getTop(self):
        temp = 'VEU'
        ret = None   
        if (self._getBestOf2(temp, "^GSPC") == "^GSPC"):
            if (self._getBestOf2("^GSPC", "TLT") == "^GSPC"):
                ret= "^GSPC"
            else:
                ret="TLT"
        elif (self._getBestOf2(temp, "TLT") == "TLT"):
            ret = "TLT"
        else:
            ret = temp
        return ret

    def _placePendingOrders(self):
        remainingCash = self.getBroker().getCash() * .8  # Use less cash just in case price changes too much.

        myTimestamp = self.getCurrentDateTime()
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
                print("%s ... Placing market order for %d %s shares" % (myTimestamp, orderSize, instrument))
#                 lastPrice = self.getLastPrice(instrument)
#                 cost = orderSize * lastPrice
#                 self.info("Remaining Cash ... %d %d" % (remainingCash,cost))
                self.marketOrder(instrument, orderSize, goodTillCanceled=True)
                self.__sharesToBuy[instrument] -= orderSize
                
                
    def _logPosSize(self):
        totalEquity = self.getBroker().getEquity()
        positions = self.getBroker().getPositions()
        for instrument in self.getBroker().getPositions():
            posSize = positions[instrument] * self.getLastPrice(instrument) / totalEquity * 100
            self.info("%s - %0.2f %%" % (instrument, posSize))

    def _rebalance(self):
#         self.info("Rebalancing")
        myTimestamp = self.getCurrentDateTime()
        print myTimestamp
#         if smashort[-1] > smalong[-1] and smashort[-1] is not None and smalong[-1] is not None:
    #         if 1:   
            # Cancel all active/pending orders.
        for order in self.getBroker().getActiveOrders():
            self.getBroker().cancelOrder(order)
        self.__sharesToBuy = {}

        # Calculate which positions should be open during the next period.
#         topByClass = self._getTop()
#         for assetClass in topByClass:
        newtop = self._getTop()
        print newtop
        print("%s ... Best for class  %s" % (myTimestamp, newtop))
        
        if newtop is not None:
            lastPrice = self.getLastPrice(newtop)
            cashForInstrument = self.getBroker().getEquity()
            # This may yield a negative value and we have to reduce this
            # position.
            self.__sharesToBuy[newtop] = int(cashForInstrument / lastPrice)

        # Calculate which positions should be closed.
        for instrument in self.getBroker().getPositions():
            if instrument != newtop:
                currentShares = self.getBroker().getShares(instrument)
                assert(instrument not in self.__sharesToBuy)
                self.__sharesToBuy[instrument] = currentShares * -1
#         else:
#             for instrument in self.getBroker().getPositions():
#                 currentShares = self.getBroker().getShares(instrument)
#         #        assert(instrument not in self.__sharesToBuy)
#                 self.__sharesToBuy[instrument] = currentShares * -1

    def getSMA(self, instrument):
        return self.__sma[instrument]

    def onBars(self, bars):
        currentDateTime = bars.getDateTime()

        if self._shouldRebalance(currentDateTime):
            self.__rebalanceMonth = currentDateTime.month
            self._rebalance()

        self._placePendingOrders()


def main(plot):
#     for x in range(100,200,10):
        initialCash = 10000
        beginYear = 2004
        
        
        endYear = date.today().year
        riskFreeRate = 0.02
        LBPs = [20,60,120,240]
        feed = yahoofeed.Feed()

    
        # Download the bars.
        instruments = ["VWESX",'^GSPC','VFINX','VEIEX']
#         for assetClass in instrumentsByClass:
#             instruments.extend(instrumentsByClass[assetClass])
#         feed = yahoofinance.build_feed(instruments, beginYear, endYear, "data", skipErrors=True)
        for instrument in instruments:
            for year in range(beginYear,endYear+1,1):
                filename = "data/%s-%d-yahoofinance.csv" % (instrument,year)
                if os.path.isfile(filename):
                    feed.addBarsFromCSV(instrument,filename)

       
        strat = MarketTiming(feed, instruments, initialCash, LBPs)
        returnsAnalyzer = returns.Returns()
        strat.attachAnalyzer(returnsAnalyzer)
        sharpeRatioAnalyzer = sharpe.SharpeRatio()
        strat.attachAnalyzer(sharpeRatioAnalyzer)
        drawDownAnalyzer = drawdown.DrawDown()
        strat.attachAnalyzer(drawDownAnalyzer)
        tradesAnalyzer = trades.Trades()
        strat.attachAnalyzer(tradesAnalyzer)
        
        if plot:
            plt = plotter.StrategyPlotter(strat, False, False, False)
            plt.getOrCreateSubplot("cash").addCallback("Cash", lambda x: strat.getBroker().getCash())
            # Plot strategy vs. SPY cumulative returns.
            plt.getOrCreateSubplot("returns").addDataSeries("VFINX", cumret.CumulativeReturn(feed["VFINX"].getPriceDataSeries()))
            plt.getOrCreateSubplot("returns").addDataSeries("Strategy", returnsAnalyzer.getCumulativeReturns())
    
        strat.run()
        #print LBPs, (returnsAnalyzer.getCumulativeReturns()[-1] * 100)/float(12)
        if (returnsAnalyzer.getCumulativeReturns()[-1] * 100)/float((endYear-1)-beginYear) > 0:
            print LBPs
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
#             for x in returns1:
#                 print x * 100
            print
            print "Profitable trades: %d" % (tradesAnalyzer.getProfitableCount())
            if tradesAnalyzer.getProfitableCount() > 0:
                profits = tradesAnalyzer.getProfits()
                print "Avg. profit: $%2.f" % (profits.mean())
                print "Profits std. dev.: $%2.f" % (profits.std())
                print "Max. profit: $%2.f" % (profits.max())
                print "Min. profit: $%2.f" % (profits.min())
                returns1 = tradesAnalyzer.getPositiveReturns()
                print "Avg. return: %2.f %%" % (returns1.mean() * 100)
                print "Returns std. dev.: %2.f %%" % (returns1.std() * 100)
                print "Max. return: %2.f %%" % (returns1.max() * 100)
                print "Min. return: %2.f %%" % (returns1.min() * 100)
             
            print
            print "Unprofitable trades: %d" % (tradesAnalyzer.getUnprofitableCount())
            if tradesAnalyzer.getUnprofitableCount() > 0:
                losses = tradesAnalyzer.getLosses()
                print "Avg. loss: $%2.f" % (losses.mean())
                print "Losses std. dev.: $%2.f" % (losses.std())
                print "Max. loss: $%2.f" % (losses.min())
                print "Min. loss: $%2.f" % (losses.max())
                returns1 = tradesAnalyzer.getNegativeReturns()
                print "Avg. return: %2.f %%" % (returns1.mean() * 100)
                print "Returns std. dev.: %2.f %%" % (returns1.std() * 100)
                print "Max. return: %2.f %%" % (returns1.max() * 100)
                print "Min. return: %2.f %%" % (returns1.min() * 100)
     
        if plot:
            plt.plot()

if __name__ == "__main__":
     main(True)
