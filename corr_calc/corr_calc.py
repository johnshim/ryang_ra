import urllib2
import numpy as np
import pylab as pl
import datetime

# Source: http://jiripik.me/2012/06/06/python-code-for-getting-market-data-from-finance-yahoo-com/

# prices = data[:,6] or prices = data[:, title.index("Adj Close")], pl.num2date(data[:,1]) back dates
# syntax http://ichart.yahoo.com/table.csv?s={Yahoo.Symbol.[isin]}&a={Von.M-1}&b={Von.T}&c={Von.J}&d={Bis.M}&e={Bis.T}&f={Bis. J}&g=d&y=0&z=jdsu&ignore=.csv
def getNumpyHistoricalTimeseries(symbol,fromDate, toDate):
    f = urllib2.urlopen('http://ichart.yahoo.com/table.csv?a='+ str(fromDate.month -1) +'&c='+ str(fromDate.year) +'&b=' + str(fromDate.day) + '&e='+  str(toDate.day) + '&d='+ str(toDate.month-1) +'&g=d&f=' + str(toDate.year) + '&s=' + symbol + '&ignore=.csv')
    header = f.readline().strip().split(",")
    return np.loadtxt(f, dtype=np.float, delimiter=",", converters={0: pl.datestr2num})


if __name__ == "__main__":
    d1 = datetime.date(2012,1,1)
    d2 = datetime.date(2012,1,5)
    n = getNumpyHistoricalTimeseries("GOOG", d1, d2)

    for i in n:
        for x in i:
            print x, 
        print '\n'
    
