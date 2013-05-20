import urllib2
import numpy as np
import pylab as pl
import datetime
import csv

def getTicks():
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



# Source: http://jiripik.me/2012/06/06/python-code-for-getting-market-data-from-finance-yahoo-com/

# prices = data[:,6] or prices = data[:, title.index("Adj Close")], pl.num2date(data[:,1]) back dates
# syntax http://ichart.yahoo.com/table.csv?s={Yahoo.Symbol.[isin]}&a={Von.M-1}&b={Von.T}&c={Von.J}&d={Bis.M}&e={Bis.T}&f={Bis. J}&g=d&y=0&z=jdsu&ignore=.csv
def getNumpyHistoricalTimeseries(symbol,fromDate, toDate):
    #print 'baz'
    f = urllib2.urlopen('http://ichart.yahoo.com/table.csv?a='+ str(fromDate.month -1) +'&c='+ str(fromDate.year) +'&b=' + str(fromDate.day) + '&e='+  str(toDate.day) + '&d='+ str(toDate.month-1) +'&g=d&f=' + str(toDate.year) + '&s=' + symbol + '&ignore=.csv')
    #print 'blah'
    header = f.readline().strip().split(",")
    #print 'bar'
    return np.loadtxt(f, dtype=np.float, delimiter=",", converters={0: pl.datestr2num})

def getStockData(symbol, fromDate, toDate):
    n = getNumpyHistoricalTimeseries(symbol, d1, d2)

    # Average daily volume over this period
    #print 'foo'
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


if __name__ == "__main__":

    #stocks = ["GOOG", "AAPL", "YHOO", "MSFT", "NFLX", "DIS", "GS", "JPM"]
    stocks = getTicks()

    d1 = datetime.date(2012,1,1)
    d2 = datetime.date(2013,1,1)

    # Get the # of entries
    try:
        obs = getStockData(stocks[0], d1, d2)[0].shape[0]
    except:
        print stocks[0]
    
    print "Stock \tVolume \tVolatility"
    returns = np.zeros([len(stocks),obs])

    for s in xrange(len(stocks)):
        try:
            x = getStockData(stocks[s], d1, d2)
        except:
            print stocks[s], " ERROR"
            continue #break
        print stocks[s], '\t', x[1], '\t', x[2]

        try:
            returns[s,:] = x[0]
        except:
            continue

    print np.corrcoef(returns)
