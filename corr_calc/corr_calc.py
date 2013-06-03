import urllib2
import numpy as np
import pylab as pl
import datetime
import csv
import sys

#####
# Functions for grabbing Tickers from file
# 
# Currently: S&P500, ETF's, Futures
#####

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

def getBBGTicks():
    bbg = open('futures_blp_ticksonly.csv', 'r')
    x = csv.reader(bbg)

    tickers = []

    for row in x:
        tickers.append(row[0])

    return tickers

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

    # load from file
    loc = '/media/sf_Dropbox/cross_OS'
    f = open(loc + '/Data/blp_data_' + symbol + '.csv')

    returns = []
    vlm = []

    for line in f:
        l = line.strip().split(',')

        if l[0] != '0':
            returns.append(float(l[0]))

        if l[1] != '0':
            vlm.append(float(l[1]))

    f.close()

    # Process
    vlm = sum(vlm) / len(vlm)
    #print vlm # avg

    returns = np.array(returns)
    diff = np.diff(returns)

    pdiff = diff / returns[1:]

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

if __name__ == "__main__":

    # Parameters
    minVolume = 1000000
    minCorr = 0.9

    BBG = False # Run Bloomberg
    YHF = True # Run Yahoo Finance

    # Load Tickers from File
    stocks = getSPTicks()
    etfs = getETFTicks()
    bbgfutures = getBBGTicks()

    stocks = stocks + etfs

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

        obs1 = getStockData(stocks[0], d1, d2)[0].shape[0]
        obs2 = getBloombergData(bbgfutures[0])[0].shape[0]
        obs = max(obs1, obs2)
    except:
        #print stocks[0]
        print bbgfutures[0]
    
    print "Ticker \tVolume \tVolatility"
    #returns = np.zeros([len(stocks),obs])
    returns = np.zeros([len(bbgfutures) + len(stocks),obs])
    
    if BBG:
        # Get Bloomberg Data (Futures for now)

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
                returns[s,:] = 100 * x[0]
            except:
                # Usual problem: ticker was not live for full year
                print bbgfutures[s], " MATRIX ERROR"
                print x[0].shape, " != obs (", obs, ")"
                returns[s,:obs] = 100 * x[0][:obs]
                continue

            # If successful, add to list of ticks that went through
            ticks[bbgfutures[s]] = {'volume':x[1], 'volatility':x[2]}
            ticklist.append(bbgfutures[s])



    if YHF:
        # Get Data from Yahoo! Finance (stocks, etfs for now)
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
                returns[s,:] = 100 * x[0]
            except:
                # Usual problem: ticker was not live for full year
                print stocks[s], " MATRIX ERROR"
                print x[0].shape, " != obs (", obs, ")"
                continue

            # If successful, add to list of ticks that went through
            ticks[stocks[s]] = {'volume':x[1], 'volatility':x[2]}
            ticklist.append(stocks[s])

    # Calculate Correlation Matrix
    corr = getCorrMatrix(returns)


    # Grab Correlations above threshold
    entries = []

    # row i, col j (upper triangle only)
    for i in xrange(corr.shape[0]):
        for j in xrange(i+1, corr.shape[1]):

            if corr[i,j] > minCorr:
                t1 = ticklist[i]
                t2 = ticklist[j]

                entry = [t1, t2, corr[i,j], ticks[t1]['volume'], ticks[t2]['volume'], ticks[t1]['volatility'], ticks[t2]['volatility']]
                entries.append(entry)

    # Print Correlations
    print "Correlations above threshold"
    for i in entries:
        print i
            

    # Write final correlation entries into CSV file
    csvout = open('corr_calc.out.csv', 'w')
    writer = csv.writer(csvout)
    writer.writerow(['Ticker1', 'Ticker2', 'Corr', 'Vlm1', 'Vlm2', 'Vol1', 'Vol2'])
    writer.writerows(entries)

    csvout.close()

    print "DONE!"
