# External packages

import tables
from tables import *

import datetime as dt
import time

import numpy
import numpy as np

from scipy import signal
from scipy import interpolate

import glob
import sys

# Ron's packages


# VARS
DATA_FOLDER = "/datastore/dbd/auction/book_data/arca/" # data folder on bushlnxeb01.chicagobooth.edu
#DATA_FOLDER = "C:\Users\Runnan\Dropbox\Work\budish_ra\data" # data folder on Laptop (Windows)
#DATA_FOLDER = "/media/sf_Dropbox/Work/budish_ra/data/"

############################
# Dan's definitions
############################

class BookTable(tables.IsDescription):
    """                                                                                                                                                                                              
    Basic book table                                                                                                                                                                                 
    """
    timestamp   = Int64Col()
    timestamp_s = StringCol(16)
    ask         = Int64Col(shape=(10,2))
    bid         = Int64Col(shape=(10,2))
    seqnum      = Int64Col()

class ImpliedBookTable(tables.IsDescription):
    """                                                                                                                                                                                              
    Basic book table                                                                                                                                                                                 
    """
    timestamp   = Int64Col()
    timestamp_s = StringCol(16)
    ask         = Int64Col(shape=(10,2))
    bid         = Int64Col(shape=(10,2))
    implied     = Int32Col()

class TradeTable(tables.IsDescription):
    timestamp   = Int64Col()
    timestamp_s = StringCol(16)
    trade_type  = Int64Col()
    price       = Int64Col()
    quantity    = Int64Col()
    seqnum      = Int64Col()

############################
############################


def filterData(input_file, product, START_TIME, END_TIME, datestr):
    # Convert to time date
    date = dt.date(int(datestr[0:4]), int(datestr[4:6]), int(datestr[6:8]))
    
    contract_name = product
    front_contract = getattr(input_file.root, contract_name)

    # Filter by time
    init = time.mktime(dt.datetime.combine(date, START_TIME).timetuple()) * 1000000
    end = time.mktime(dt.datetime.combine(date, END_TIME).timetuple()) * 1000000

    selected_books = front_contract.books.readWhere('(timestamp >= init) & (timestamp <= end)')
    
    return [selected_books, init, end]

def toTimeSpace(books, init, end):
    # Extract the relevant timestamps

    a = time.time()

    times1000 = books['timestamp']
    times = times1000 / 1000 # scale to milliseconds

    # Scale init, end
    init = init / 1000
    end = end / 1000

    # total number of milliseconds
    total_interval = end - init

    # Offset for times
    offset = times[0]

    preset = times[0] - init
    postset = end - times[-1]

    # timemidpts: array of midpoint prices
    timemidpts = numpy.zeros(total_interval + 1)

    # Holds time of latest book update
    oldUpdateTime = times[0]
    oldPrice = 0

    # Precompute midpoints from best bid / best ask
    bestasks = np.array([y[0,0] for y in books['ask']])
    bestbids = np.array([y[0,0] for y in books['bid']])
    midpts = (bestasks + bestbids) / 2.0

    b = time.time()
    print "Sec1 time: \t ", b - a

    idx = np.searchsorted(times, np.array(range(int(init), int(end)+1)), side='left')
    timemidpts = midpts[idx-1]

    
    #f = interpolate.interp1d(times, midpts, kind='linear', bounds_error=False, fill_value=midpts[0])
    

    #timemidpts = f(alltimes)
    #timemidpts = np.interp(alltimes, times, midpts)
    """
    # i is index of book update
    for i in xrange(len(times)):
    #for i in xrange(20000):
        # t is timestamp of latest book update
        t = times[i]

        # If same time as previous update
        if t == oldUpdateTime:
            # Update book at that time
            #timemidpts[t - offset + preset] = (books[i]['ask'][0,0] + books[i]['bid'][0,0]) / 2.0
            timemidpts[t - offset + preset] = midpts[i]

        # If gap in updates, we need to replicate old price
        elif t > oldUpdateTime:
            # Copy old time for diff times
            timemidpts[oldUpdateTime - offset + preset : t - offset + preset] = oldPrice

            # Update book at new time
            #timemidpts[t - offset + preset] = (books[i]['ask'][0,0] + books[i]['bid'][0,0]) / 2.0
            timemidpts[t - offset + preset] = midpts[i]
        else:
            print "ERROR"

        # Update previous update time/price
        oldUpdateTime = t
        #oldPrice = (books[i]['ask'][0,0] + books[i]['bid'][0,0]) / 2.0
        oldPrice = midpts[i]
        
    # Fill in beginning and end
    #timemidpts[0 : preset] = (books[0]['ask'][0,0] + books[0]['bid'][0,0]) / 2.0
    
    print "Sec2 time: \t ", time.time() - b
    timemidpts[0 : preset] = midpts[0]

    #timemidpts[times[-1] - offset + preset : len(timemidpts)] = (books[-1]['ask'][0,0] + books[-1]['bid'][0,0]) / 2.0
    timemidpts[times[-1] - offset + preset : len(timemidpts)] = midpts[-1]
    """
    return timemidpts

def toTimeSpaceInterpolate(books, init, end):
    # Construct xold, yold
    return 0

def getDifferenceArray(timemidpts, interval):

    # PD = avg midpt over (t,t+k) - avg midpt over (0,t)

    ret = np.cumsum(timemidpts, dtype=float)
    mv = (ret[interval - 1:] - ret[:1 - interval]) / interval

    return np.diff(mv)


def printCorrCoefMatrix(corr, products):
    print '\t',
    for i in products:
        print i, '\t',
    print '\n'
    for i in xrange(len(products)):
        print products[i], '\t',
        for j in xrange(len(products)):
            print "{0:.2f}".format(corr[i,j]),
            print '\t',
        print '\n'


def writeCorrCoefMatrix(corr, valid_products, interval, datestr, products):

    outstr = ""
    for i in xrange(len(valid_products)):
        for j in xrange(len(valid_products)):
            outstr = outstr + valid_products[i] + "," + valid_products[j] + "," + "{0:.8f}".format(corr[i,j]) + "\n"    

    f = open("corr" + "_" + str(interval) + "_" + datestr + "_" + ''.join(products) + ".csv", 'w')
    f.write(outstr)

    f.close()

###########
# MAIN
###########


if __name__ == "__main__":
    print "Computing Regressions"

    # Set Parameters
    try:
        yr = sys.argv[1]
        #mth = sys.argv[2]
        #dates = glob.glob(DATA_FOLDER + yr + mth + '*')
        dates = glob.glob(DATA_FOLDER + yr + '*')
    except:
        dates = []
    dates = ['/datastore/dbd/auction/book_data/arca/20111017_TOP.h5']

    try:
        interval = int(sys.argv[2])
    except:
        interval = 60000 # in milliseconds

    stock_list = ['XHB' , 'NYX' , 'XLK' , 'IBM' , 'CVX' , 'VHT' , 'AAPL' , 'DIA' , 'VDC' , 'BP' , 'BAC' , 'XLY' , 'XLV' , 'MSFT' , 'XLP' , 'VPU' , 'SPY' , 'PG' , 'VNQ' , 'XLF' , 'CME' , 'HD' , 'GOOG' , 'C' , 'GS' , 'XLE' , 'XLB' , 'GE' , 'VGT' , 'JPM' , 'XOM' , 'VAW' , 'PFE' , 'CSCO' , 'VCR' , 'VIS' , 'QQQ' , 'MS' , 'JNJ' , 'VOX' , 'LOW' ]

    # For each stock, we need to do the following
    #products = stock_list
    #products = ['AAPL', 'XOM', 'GE', 'JNJ', 'IBM', 'DIA']
    products = ['AAPL', 'XOM', 'GE', 'JNJ', 'IBM', 'DIA']
    #products = ['AAPL','GOOG']

    for date in dates:
        valid_products = []

        print "Processing ", date

        datestr = date[38:46]

        # Skip if already processed
        if len(glob.glob('*' + str(interval) '_*' + datestr + '_*' + ''.join(products) + '*')) != 0:
            print date, " already done."
            continue

        # TEMP FOR TESTING ONLY
        # datestr = '20111017'

        filename = datestr + "_TOP.h5" # "20111017_TOP.h5"

        start = time.time()

        # Load file
        input_file = tables.openFile(DATA_FOLDER + filename)

        loaddone = time.time()
        print "load time:\t", loaddone - start

        ## Filter for stock

        START_TIME = dt.time(8, 30, 00, 0) # 1430 GMT = 9:30AM Eastern
        END_TIME = dt.time(14, 00, 00, 0) # 2000 GMT = 3:00PM Eastern
    
        for i in xrange(len(products)):
                #print "Processing ", products[i]
                #try:
                product = products[i]

                temp = filterData(input_file, product, START_TIME, END_TIME, datestr)

                filterdone = time.time()
                if i == 0:
                    print "filter time:\t", filterdone - loaddone
                else:
                    print "filter time:\t", filterdone - timespacedone

                # break up temp
                books = temp[0]
                init = temp[1]
                end = temp[2]
                        
                timemidpts = toTimeSpace(books, init, end)

                timespacedone = time.time()
                print "tspace time:\t", timespacedone - filterdone

                diffstart = time.time()
                if i == 0:
                    pd = getDifferenceArray(timemidpts, interval)            
                else:
                    pd = np.vstack((pd, getDifferenceArray(timemidpts, interval)))
                diffdone = time.time()
                print "diff time:\t", diffdone - diffstart
                    

                """
                    try:
                        #pd[i,:] = getDifferenceArray(timemidpts, interval)

                        print "CONCAT"
                    except:
                        #print [len(valid_products), len(timemidpts) - interval]
                        #pd = np.zeros([len(valid_products), len(timemidpts) - interval])
                        #pd[i,:] = getDifferenceArray(timemidpts, interval)            

                        print "NEW"
                """
                valid_products.append(product)
                #except:
                #print products[i], 'failed'

                
        #print pd

        # Take correlation across stocks
        try:
            corr = np.corrcoef(pd)
            corrdone = time.time()
            print "corr time:\t", corrdone - diffdone
            
        # Display correlation matrix
            printCorrCoefMatrix(corr, valid_products)

        #writeCorrCoefMatrix(corr, valid_products, interval, datestr, products)

        # Clean up
            input_file.close()
        except:
            input_file.close)(
