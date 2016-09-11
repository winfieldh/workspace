import sma_crossover
from pyalgotrade import plotter
from pyalgotrade.tools import yahoofinance
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.barfeed import yahoofeed
import os
from datetime import date
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import trades

def main(plot):
    instrument = "SPY"
    beginYear = 2000
    endYear = date.today().year
    thisMonth = date.today().month
    riskFreeRate = 0.02
    initialCash = 10000
    # Download the bars.    
   
    for x in range(20,30,10):
        smaPeriod = x  
        feed = yahoofeed.Feed()
        for year in range(beginYear,endYear+1,1):
            filename = "data/%s-%d-yahoofinance.csv" % (instrument,year)
            if os.path.isfile(filename):
                feed.addBarsFromCSV(instrument,filename)
  
 #      feed = yahoofinance.build_feed([instrument], beginYear, endYear, ".")
        strat = sma_crossover.SMACrossOver(feed, instrument, smaPeriod, initialCash)
        sharpeRatioAnalyzer = sharpe.SharpeRatio()
        strat.attachAnalyzer(sharpeRatioAnalyzer)
        returnsAnalyzer = returns.Returns()
        strat.attachAnalyzer(returnsAnalyzer)
        drawDownAnalyzer = drawdown.DrawDown()
        strat.attachAnalyzer(drawDownAnalyzer)
        tradesAnalyzer = trades.Trades()
        strat.attachAnalyzer(tradesAnalyzer)

#         if plot:
#             plt = plotter.StrategyPlotter(strat, True, False, True)
#             plt.getInstrumentSubplot(instrument).addDataSeries("sma", strat.getSMA())
    
        strat.run()
        AvgAnnRet = (returnsAnalyzer.getCumulativeReturns()[-1] * 100)/float((endYear-beginYear) + (thisMonth/12))
        if (AvgAnnRet) > 5:
            print "SMA Period: %d. Sharpe ratio: %.2f" % (smaPeriod,sharpeRatioAnalyzer.getSharpeRatio(0.05))
            print "Final portfolio value: $%.2f" % strat.getResult()
            print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(riskFreeRate)
            print "Cumulative Returns: %.2f %%" % (returnsAnalyzer.getCumulativeReturns()[-1] * 100)
#             AvgAnnRet = (returnsAnalyzer.getCumulativeReturns()[-1] * 100)/float((endYear-1)-beginYear)
            print "Average Annual Returns: %.2f %%" % AvgAnnRet
            print "Max. drawdown: %.2f %%" % (drawDownAnalyzer.getMaxDrawDown() * 100)
            print "Longest drawdown duration: %s" % (drawDownAnalyzer.getLongestDrawDownDuration())
            print
            print "Total trades: %d" % (tradesAnalyzer.getCount())

#         if plot:
#             plt.plot()
    

if __name__ == "__main__":
    main(True)