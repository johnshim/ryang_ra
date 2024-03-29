import urllib2
import numpy as np
import pylab as pl
import datetime
import csv
import sys

#####
# CONTROLS
#####


BBG = False # Run Bloomberg
YHF = True # Run Yahoo Finance (S&P 500, ETFs)

# Parameters
minVolume = 50000000
minCorr = 0.9
    
#####
#####








#####
# Functions for grabbing Tickers from file
# 
# Currently: S&P500, ETF's, Futures
#####

def getSPTicks():
    SP = open('SP500.csv', 'r')
    x = csv.reader(SP)

    tickers = []
    desc = []

    for row in x:
        try:
            assert row[2] != 'Constituent Symbol'
            tickers.append(row[2].replace(" ",""))
            desc.append(row[1])
        except:
            continue

    return [tickers, desc]

def getETFTicks():
    ETF = open('etf.csv', 'r')
    x = csv.reader(ETF)

    tickers = []
    desc = []

    for row in x:
        tickers.append(row[0])
        desc.append(row[1])

    return [tickers, desc]

def getBBGTicks():
    bbg = open('futures_blp_ticksonly.csv', 'r')
    x = csv.reader(bbg)

    tickers = []
    desc = []

    for row in x:
        tickers.append(row[0])
        desc.append(row[1])

    return [tickers, desc]

######
# Begin External Code
# Source: http://jiripik.me/2012/06/06/python-code-for-getting-market-data-from-finance-yahoo-com/
######

# prices = data[:,6] or prices = data[:, title.index("Adj Close")], pl.num2date(data[:,1]) back dates
# syntax http://ichart.yahoo.com/table.csv?s={Yahoo.Symbol.[isin]}&a={Von.M-1}&b={Von.T}&c={Von.J}&d={Bis.M}&e={Bis.T}&f={Bis. J}&g=d&y=0&z=jdsu&ignore=.csv

def getNumpyHistoricalTimeseries(symbol,fromDate, toDate):
    url = 'http://ichart.yahoo.com/table.csv?a='+ str(fromDate.month -1) +'&c='+ str(fromDate.year) +'&b=' + str(fromDate.day) + '&e='+  str(toDate.day) + '&d='+ str(toDate.month-1) +'&g=d&f=' + str(toDate.year) + '&s=' + symbol + '&ignore=.csv'
    f = urllib2.urlopen(url)
    header = f.readline().strip().split(",")
    return np.loadtxt(f, dtype=np.float, delimiter=",", converters={0: pl.datestr2num})

######
# End External Code
######

######
# Get Stocks/ETFs from Yahoo Finance
######

def getStockData(symbol, fromDate, toDate):
    n = getNumpyHistoricalTimeseries(symbol, fromDate, toDate)

    # Average daily volume over this period
    volume = np.dot(n[:,5], n[:, 4]) / n[:,5].shape[0]

    # Daily Percentage Returns
    close = n[:,4]
    adjclose = n[:,6]
    diff = np.diff(close)
    try:
        pd = diff / close[1:]
    except:
        pd = diff

    # SD of returns over this period
    try:
        volatility = np.std(pd)
    except:
        volatility = 0

    return (pd, volume, volatility, close, adjclose)

#####
# Get Data from Bloomberg
# Notes: Currently only reading from csv files since
#        this script is not running on Bloomberg terminal
#####

def getBloombergData(symbol):

    print 'getting ', symbol

    # load from file
    loc = '/home/ryang8/budish_ra/corr_calc/'
    fn = loc + 'Data/blp_data_' + symbol + '.csv'
    f = open(fn)

    settle = []
    vlm = []

    for line in f:

        l = line.strip().split(',')
        if l[1] != '0':
            settle.append(float(l[1]))


        if l[2] != '0':
            vlm.append(float(l[2]))


    f.close()

    # Process
    vlm = np.array(vlm)

    settle = np.array(settle)

    # Multiply by price, average over days
    # vlm already scaled by nominal values
    vlm = np.dot(vlm, settle) / vlm.shape[0]


    diff = np.diff(settle)

    pdiff = diff / settle[1:]

    vol = np.std(pdiff)

    return (pdiff, vlm, vol)

#####
# getCorrMatrix(returns, write)
# Description: Calculates correlation matrix of returns data,
#              filtering out empty rows and writing
#####


def getCorrMatrix(returns, write=False):

    # Filter out all tickers with errors
    returns = returns[~np.all(returns == 0, axis = 1)]

    if (write == True):
        np.savetxt("corr_calc.corrmatrix", returns, delimiter=',')

    return np.corrcoef(returns)

#####
# MAIN FUNCTION
#
#
#####


if __name__ == "__main__":



    # Load Tickers from File
    x = getSPTicks()
    stocks = x[0]
    stockdesc = {}
    for i in xrange(len(stocks)):
        stockdesc[x[0][i]] = x[1][i]

    x = getETFTicks()
    etfs = x[0]
    etfdesc = {}

    for i in xrange(len(etfs)):
        etfdesc[x[0][i]] = x[1][i]

    x = getBBGTicks()
    bbgfutures = x[0]
    futuresdesc = {}

    for i in xrange(len(bbgfutures)):
        futuresdesc[x[0][i]] = x[1][i]

    print type(stocks)
    print type(etfs)
    stocks = stocks + etfs

    #stocks = ["SPY"]
    
    # Set start, end dates
    d1 = datetime.date(2011,1,1)
    d2 = datetime.date(2011,12,31)

    # Initiate other 
    ticks = {}
    ticklist = []


    # Get the # of entries
    try:
        # Note: this is problematic, different goods seem to
        #       have different numbers of entries

        if YHF:
            obs1 = getStockData(stocks[0], d1, d2)[0].shape[0]

        if BBG:
            print '-', bbgfutures[0]
            obs2 = getBloombergData(bbgfutures[0])[0].shape[0]
        #obs2 = 10

        if YHF:
            obs = obs1
        if BBG:
            obs = obs2
        if YHF and BBG:
            obs = max(obs1, obs2)

        print "OBS: ", obs

        #print obs1, obs2, obs
    except:
        #print stocks[0]
        print bbgfutures[0]
        print obs1
        print obs2
        print obs
        sys.exit()
    
    print "Ticker \tVolume \tVolatility"
    #returns = np.zeros([len(stocks),obs])
    returns = np.zeros([len(bbgfutures) + len(stocks),obs])
    
    prev = 0


    if BBG:
        # Get Bloomberg Data (Futures for now)
        #bbgfutures = ['ES1 Index']
        for s in xrange(len(bbgfutures)):

            print "currently getting ", bbgfutures[s]

            try:
                x = getBloombergData(bbgfutures[s])
            except:
                # Usual problem: ticker was not live for full year
                print bbgfutures[s], " ERROR"
                continue


            # Filter for volume threshold
            if x[1] < minVolume:
                continue

            print bbgfutures[s], '\t', x[1], '\t', x[2]

            try:
                returns[s,:] = x[0]
            except:
                # Usual problem: ticker was not live for full year
                print bbgfutures[s], " MATRIX ERROR"
                print x[0].shape, " != obs (", obs, ")"
                #returns[s,:obs] = x[0][:obs]
                continue

            # If successful, add to list of ticks that went through
            ticks[bbgfutures[s]] = {'volume':x[1], 'volatility':x[2]}
            ticklist.append(bbgfutures[s])
        prev = len(bbgfutures)


    if YHF:
        # Get Data from Yahoo! Finance (stocks, etfs for now)
        #stocks = ['SPY']
        for s in range(len(stocks)):

            try:
                x = getStockData(stocks[s], d1, d2)
            except:
                # Usual problem: ticker was not live for full year
                print stocks[s], " ERROR"
                continue


            # Filter for volume threshold
            if x[1] < minVolume:
                continue

            print stocks[s], '\t', x[1], '\t', x[2]

            try:
                returns[prev + s,:] = x[0]
            except:
                # Usual problem: ticker was not live for full year
                print stocks[s], " MATRIX ERROR"
                print x[0].shape, " != obs (", obs, ")"
                continue

            # If successful, add to list of ticks that went through
            ticks[stocks[s]] = {'volume':x[1], 'volatility':x[2]}
            ticklist.append(stocks[s])

    #print returns
    print ticks
    # Calculate Correlation Matrix
    corr = getCorrMatrix(returns)
    # try ES-SPY correlation
    #est = ticklist.index('ES1 Index')
    #spyt = ticklist.index('SPY')
    #print corr[est,spyt]
    #print corr
    
    print corr.shape[0], ' and ', corr.shape[1], ' vs ', len(ticklist)

    # Grab Correlations above threshold
    entries = []

    # row i, col j (upper triangle only)
    for i in xrange(corr.shape[0]):
        for j in xrange(i+1, corr.shape[1]):

            if corr[i,j] > minCorr:
                t1 = ticklist[i]
                t2 = ticklist[j]

                # Get longer Descriptions
                try:
                    desc1 = stockdesc[t1]
                except:
                    try:
                        desc1 = etfdesc[t1]
                    except:
                        desc1 = futuresdesc[t1]

                try:
                    desc2 = stockdesc[t2]
                except:
                    try:
                        desc2 = etfdesc[t2]
                    except:
                        desc2 = futuresdesc[t2]


                entry = [t1, desc1, t2, desc2, corr[i,j], ticks[t1]['volume'], ticks[t2]['volume'], ticks[t1]['volatility'], ticks[t2]['volatility']]
                entries.append(entry)

    # Print Correlations
    print "Correlations above threshold"
    for i in entries:
        print i
            

    # Write final correlation entries into CSV file
    csvout = open('Correlations.csv', 'w')
    writer = csv.writer(csvout)
    writer.writerow(['Ticker1', 'Ticker2', 'Corr', 'Vlm1', 'Vlm2', 'Vol1', 'Vol2'])
    writer.writerows(entries)

    csvout.close()

    print "DONE!"
