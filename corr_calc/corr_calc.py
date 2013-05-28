import urllib2
import numpy as np
import pylab as pl
import datetime
import csv
import sys

def getSPTicks():
    SP = open('SP500.csv', 'r')
    x = csv.reader(SP)

    tickers = []

    for row in x:
        try:
            assert row[2] != 'Constituent Symbol'
            tickers.append(row[2].replace(" ",""))
        except:
            continue

    return tickers

def getETFTicks():
    ETF = open('etf.csv', 'r')
    x = csv.reader(ETF)

    tickers = []

    for row in x:
        tickers.append(row[0])

    return tickers

def getFuturesTicks():
    futures = open('futures.csv', 'r')
    x = csv.reader(futures)

    tickers = []

    for row in x:
        tickers.append(row[0])

    return tickers

#
# Begin External Code
# Source: http://jiripik.me/2012/06/06/python-code-for-getting-market-data-from-finance-yahoo-com/
#

# prices = data[:,6] or prices = data[:, title.index("Adj Close")], pl.num2date(data[:,1]) back dates
# syntax http://ichart.yahoo.com/table.csv?s={Yahoo.Symbol.[isin]}&a={Von.M-1}&b={Von.T}&c={Von.J}&d={Bis.M}&e={Bis.T}&f={Bis. J}&g=d&y=0&z=jdsu&ignore=.csv

def getNumpyHistoricalTimeseries(symbol,fromDate, toDate):
    f = urllib2.urlopen('http://ichart.yahoo.com/table.csv?a='+ str(fromDate.month -1) +'&c='+ str(fromDate.year) +'&b=' + str(fromDate.day) + '&e='+  str(toDate.day) + '&d='+ str(toDate.month-1) +'&g=d&f=' + str(toDate.year) + '&s=' + symbol + '&ignore=.csv')
    header = f.readline().strip().split(",")
    return np.loadtxt(f, dtype=np.float, delimiter=",", converters={0: pl.datestr2num})

#
# End External Code
#

#####
# Get Stocks/ETFs from Yahoo Finance
#####

def getStockData(symbol, fromDate, toDate):
    n = getNumpyHistoricalTimeseries(symbol, d1, d2)

    # Average daily volume over this period
    volume = np.mean(n[:,5])
    close = n[:,4]
    diff = np.diff(close)
    try:
        pd = diff / close[:-1]
    except:
        pd = diff

    # SD of returns over this period
    try:
        volatility = np.std(pd)
    except:
        volatility = 0

    return (pd, volume, volatility)

#####
# Get Futures from Quandl
#####


def getQuandlFuturesData(symbol, d1, d2):

    year1 = str(d1.year)
    if d1.month > 9:
        month1 = str(d1.month)
    else:
        month1 = "0" + str(d1.month)
    if d1.day > 9:
        day1 = str(d1.day)
    else:
        day1 = "0" + str(d1.day)

    year2 = str(d2.year)
    if d2.month > 9:
        month2 = str(d2.month)
    else:
        month2 = "0" + str(d2.month)
    if d2.day > 9:
        day2 = str(d2.day)
    else:
        day2 = "0" + str(d2.day)

    auth = "nJUsp4WDihQVBHDyqbPn"
    url = "http://www.quandl.com/api/v1/datasets/OFDP/FUTURE_" + symbol + "1.csv?&trim_start=" + year1 + "-" + month1 + "-" + day1 + "&trim_end=" + year2 + "-" + month2 + "-" + day2 + "&sort_order=desc&auth_token=" + auth
    #print url

    f = urllib2.urlopen(url)
    head = f.readline().strip().split(",")
    try:
        data = np.loadtxt(f, dtype=np.float, delimiter=",", converters={0: pl.datestr2num})
    except:
        print symbol, " NOTHING"
    
    return data

def getFuturesData(symbol, d1, d2):

    data = getQuandlFuturesData(symbol, d1, d2)
    
    volume = np.mean(data[:,5])
    settle = data[:,4]
    
    diff = np.diff(settle)
    pd = diff / settle[:-1]
    
    volatility = np.std(pd)

    return (pd, volume, volatility)

def getCorrMatrix(returns, write=False):

    # Filter out all tickers with errors
    returns = returns[~np.all(returns == 0, axis = 1)]

    if (write == True):
        np.savetxt("corr_calc.out", returns, delimiter=',')

    return np.corrcoef(returns)

if __name__ == "__main__":

    e = []

    # Parameters
    minVolume = 10000000
    minCorr = 0.7

    stocks = getSPTicks()
    ticks = []

    etfs = getETFTicks()

    futures = getFuturesTicks()

    stocks = stocks + etfs

    d1 = datetime.date(2011,1,1)
    d2 = datetime.date(2012,1,1)

    # Get the # of entries
    try:
        #obs = getStockData(stocks[0], d1, d2)[0].shape[0]
        obs = getFuturesData(futures[0], d1, d2)[0].shape[0]
    except:
        print futures[0]
        #print stocks[0]
    
    print "Ticker \tVolume \tVolatility"
    #returns = np.zeros([len(stocks),obs])
    returns = np.zeros([len(futures),obs])
    
    ticks = {}
    ticklist = []

    #for s in xrange(len(stocks)):
    for s in xrange(len(futures)):

        print "currently getting ", futures[s]

        try:
            #x = getStockData(stocks[s], d1, d2)
            x = getFuturesData(futures[s], d1, d2)
        except:
            e.append(futures[s])
            print futures[s], " ERROR"
            # Usual problem: ticker was not live for full year
            #sys.exit()
            #print stocks[s], " ERROR"
            continue


        #
        # Filter for volume threshold
        #
        #if x[1] < minVolume:
        #    continue

        #print stocks[s], '\t', x[1], '\t', x[2]
        print futures[s], '\t', x[1], '\t', x[2]

        try:
            returns[s,:] = 100 * x[0]
        except:
            # Usual problem: ticker was not live for full year
            print stocks[s], " MATRIX ERROR"
            continue

        # If successful, add to list of ticks that went through
        #ticks[stocks[s]] = {'volume':x[1], 'volatility':x[2]}
        ticks[futures[s]] = {'volume':x[1], 'volatility':x[2]}
        #ticklist.append(stocks[s])
        ticklist.append(futures[s])



    print returns

    corr = getCorrMatrix(returns)
    print corr
    
    entries = []

    # row i, col j (upper triangle only)
    for i in xrange(corr.shape[0]):
        for j in xrange(i+1, corr.shape[1]):
            if corr[i,j] > minCorr:
                t1 = ticklist[i]
                t2 = ticklist[j]
                entries.append([t1, t2, corr[i,j], ticks[t1]['volume'], ticks[t2]['volume'], ticks[t1]['volatility'], ticks[t2]['volatility']])


    print "Correlations above threshold"
    for i in entries:
        print i
            
    csvout = open('corr_calc.out.csv', 'w')
    writer = csv.writer(csvout)
    writer.writerow(['Ticker1', 'Ticker2', 'Corr', 'Vlm1', 'Vlm2', 'Vol1', 'Vol2'])
    writer.writerows(entries)

    csvout.close()

    print "SUCCESS!"
    print e
