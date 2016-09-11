#!/usr/bin/python
from pyalgotrade import bar
from pyalgotrade.tools import yahoofinance
from datetime import date
import os, fnmatch
import glob 


def findReplace(directory, find, replace, filePattern):
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in fnmatch.filter(files, filePattern):
            filepath = os.path.join(path, filename)
            with open(filepath) as f:
                s = f.read()
            s = s.replace(find, replace)
            with open(filepath, "w") as f:
                f.write(s)

 
beginYear = 2000

#endYear = date.today().year
endYear = 2016
directory = "data"
instruments = ["SPY"] #     
# files = glob.glob("data/*%s*" % endYear)
# for f in files:
#     os.remove(f)
 
instrumentsByClass = {
  #                     "temp": ["MSCI"],
                      #                     "FIDSELECTS": ["FWRLX","FSUTX","FSRFX","FSTCX","FSPTX","FSCSX","FSRPX","FPHAX","FNARX","FSNGX","FBMPX","FSMEX","FSHCX","FSDPX","FDLSX","FBSOX","FSPCX","FCYIX","FSCGX","FSPHX","FSAGX","FIDSX","FSLEX","FSESX","FSENX","FSELX","FSDAX","FDFAX","FSVLX","FSCPX","FSDCX","FSCHX","FSLBX","FBIOX","FSRBX","FSAVX","FSAIX","FIUIX"],
                        "iShareSectors": ["IAU","ITB","IHE","IHI","IHF","IAT","IEO","ITA","IEZ","IAI","IAK","REM","REZ","FTY","SOXX","IBB","ICF","IYM","IYK","IYG","IYC","IYJ","IYE","IYH","IDU","IYR","IYZ","IYF","IYW","IYT"],
                        "iSharesMSCI":["EWG","EWU","EWH","EWC","EWW","EWA","EWP","EWL","EWI","EWS","EWM","EWD","EWQ","EWK","EWN","EWO","EWY","EWT","EWZ","EZU","EFA","EPP","EZA","EEM","KLD","EFV","EFG","DSI","BKF","ECH","IEUS","SCZ","TOK","SCJ","ACWI","ACWX","TUR","THD","EIS","AAXJ","EPU","EUFN","EIDO","EIRL","EUSA","EPOL","ENZL","EPHE","ECNS","EWZS","ERUS","MCHI","EEMS","USMV","ACWV","EEMV","EFAV","URTH","EEML","ENOR","EDEN","EWGS","EWUS","PICK","RING","VEGI","FILL","SLVP","INDA","EEMA","SMIN","EMEY","FM","VLUE","MTUM","SIZE","ICOL","QUAL","HEFA","HEWG","HEWJ","UAE","QAT","JPMV","EUMV","AXJV","HEZU","HEEM","EMHZ","CRBN","IMTM","IQLT"],
                        "Dev1": ["GLD","AXJL","EDV","EWJ","ILF","IEV","IWM","VFINX"],
                        "iShareMorningStar":["JKE","JKD","JKG","JKL","JKF","JKH","JKJ","JKI","JKK","IYLD"],
#                      "iSharesCore": ["IVV","IJH","IJR","IEMG","HDV","IEFA","ITOT","IXUS","CRED","GOVT","IUSV","IUSG","AOR","IEUR","IUSB","IPAC","AOA","AOM","ISTB","ILTB","AOK","DGRO","GNMA"],
# #                     "VanguardMFs":["VEIEX","VTSMX","VGPMX","VGSIX"],
#                     "iSharesGlobal":["KXI","IXC","IXG","IXJ","EXI","IGF","MXI","REET","IXN","IXP","WOOD","JXI"],
#                     "FredUncorrelated": ["PCY","BKLN","PVI","AMJ","DBS","DBB","DBO","DBA","DBV","PSAU","UDN","UUP","DBE","DGL","TIP","PSR","DBC"]
#                     "VanguardMFs":["VEIEX","VTSMX","VGPMX","VGSIX"],#emerging market, us market, emergin bond, long term bond,precious metal, realestate
#                     "DJ30": ["AXP","BA","CAT","CSCO","CVX","DD","DIS","GE","GS","HD","IBM","INTC","JNJ","JPM","KO","MCD","MMM","MRK","MSFT","NKE","PFE","PG","T","TRV","UNH","UTX","V","VZ","WMT","XOM"],#                                  "IVY":["VTI","VB","VEU","VWO","BND","TIP","VNQ","RWX","DBC","GSG"] 
#                     "MaxVol":["ZIV","VXZ"],
#                     #                      "USBonds": ["AGG","LQD","HYG","TIP","CSJ","SHY","MBB","CIU","IEF","TLT","SHV","MUB"] ,
#                      "IntlBonds": ["EMB","IGOV","ISHG","ITIP","GTIP","LEMB"],
#                      "CommSpec": ["DVY","SLV","GSG","DSI","PFF","QUAL","HEWG","IFGL","VLUE","HEZU","MTUM","KLD","COMT","HEWJ","IYLD","SIZE","PICK","WPS"],
#                        "Global": ["EFA","IDV","SCZ","EFV","EEM","EEMV","BKF","AAXJ","EPP","AIA","EEMA","EZU","EUFN"],
#                     "VanguardSelect": ["VBTLX","VTABX","VTIAX","VTSAX","VFICX","VTAPX","VFSTX","VWSTX","VBIAX","VWINX","VFIAX","VEXPX","VIMAX","VMRGX","VSMAX","VWNFX","VEMAX","VWIGX","VTRIX"],
#                   "Nasdaq":["AAL","AAPL","ADBE","ADI","ADP","ADSK","AKAM","ALTR","ALXN","AMAT","AMGN","AMZN","ATVI","AVGO","BBBY","BIDU","BIIB","BRCM","CA","CELG","CERN","CHKP","CHRW","CHTR","CMCSA","CMCSK","COST","CSCO","CTRX","CTSH","CTXS","DISCA","DISCK","DISH","DLTR","DTV","EA","ESRX","EXPD","FAST","FB","FISV","FOX","FOXA","GILD","GMCR","GOOG","GOOGL","GRMN","HSIC","ILMN","INTC","INTU","ISRG","KHC","KLAC","LBTYA","LBTYK","LLTC","LMCA","LMCK","LRCX","LVNTA","MAR","MAT","MDLZ","MNST","MSFT","MU","MYL","NFLX","NTAP","NVDA","NXPI","ORLY","PAYX","PCAR","PCLN","PYPLV","QCOM","QVCA","REGN","ROST","SBAC","SBUX","SIAL","SIRI","SNDK","SPLS","SRCL","STX","SYMC","TRIP","TSCO","TSLA","TXN","VIAB","VIP","VOD","VRSK","VRTX","WBA","WDC","WFM","WYNN","XLNX","YHOO"]
# "CalcRollReturn":[ "VFINX","VASIX","VASGX","VSMGX","VSCGX","VFITX"],
#                   "GMR": ["MDY","TLT","EEM","ILF","EPP","FEZ"]
 #                   "Faber": ["SPY","TLT","IYR","GLD"]
                    }
for assetClass in instrumentsByClass:
    instruments.extend(instrumentsByClass[assetClass])

#Delete current year data to ensure we download most recent
for instrument in instruments:
    filename = "./data/%s-%d-yahoofinance.csv" % (instrument,endYear)
    if (os.path.isfile(filename)):
        os.remove(filename)
        print "Removing %s " % (filename)
#     yahoofinance.download_daily_bars(instrument, year, filename, skipErrors=True)
# 
feed = yahoofinance.build_feed(instruments, beginYear, endYear, "data/", skipErrors=True)
#Fidelity data does not have volume so we create volume to allow testing to run
# for instrument in instruments:
#     filename = "%s-%d-yahoofinance.csv" % (instrument,endYear)
#     print "replacing zeros %s " % (filename)
#     findReplace('data',',000,',',1000000,',filename)
# print "Update Complete..."
for instrument in instruments:
    for year in range(beginYear,endYear+1,1):
        filename = "data/%s-%d-yahoofinance.csv" % (instrument,year)
        print "replacing zeros %s " % (filename)
        findReplace('data',',000,',',1000000,',filename)
print "Update Complete..."   

exit
