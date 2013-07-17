# External packages

import tables
from tables import *

import datetime as dt
import time

import numpy
import numpy as np

import glob
import sys

# Ron's packages


# VARS
DATA_FOLDER = "/datastore/dbd/auction/book_data/arca/"

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

def toTimeSpace(books, START_TIME, END_TIME, init, end):
    # Extract the relevant timestamps

    times1000 = books['timestamp']
    times = times1000 / 1000

    # Scale init, end
    init = init / 1000
    end = end / 1000

    #print times[0], times[-1]


    #print START_TIME, END_TIME
    #print '%f' % (init / 1000), '%f' % (end / 1000)

    # total number of milliseconds
    total_interval = times[-1] - times[0]
    #print total_interval
    total_interval = end - init
    #print total_interval

    # Offset for times
    offset = times[0]

    preset = times[0] - init
    postset = end - times[-1]

    # timemidpts: array of midpoint prices
    timemidpts = numpy.zeros(total_interval + 1)

    # Holds time of latest book update
    oldUpdateTime = times[0]
    oldPrice = 0

    # i is index of book update
    for i in xrange(len(times)):
    #for i in xrange(20000):
        # t is timestamp of latest book update
        t = times[i]

        # If same time as previous update
        if t == oldUpdateTime:
            # Update book at that time
            timemidpts[t - offset + preset] = (books[i]['ask'][0,0] + books[i]['bid'][0,0]) / 2.0

        # If gap in updates, we need to replicate old price
        elif t > oldUpdateTime:
            # Copy old time for diff times
            timemidpts[oldUpdateTime - offset + preset : t - offset + preset] = oldPrice

            # Update book at new time
            timemidpts[t - offset + preset] = (books[i]['ask'][0,0] + books[i]['bid'][0,0]) / 2.0
        else:
            print "ERROR"

        # Update previous update time/price
        oldUpdateTime = t
        oldPrice = (books[i]['ask'][0,0] + books[i]['bid'][0,0]) / 2.0

    # Fill in beginning and end
    timemidpts[0 : preset] = (books[0]['ask'][0,0] + books[0]['bid'][0,0]) / 2.0
    timemidpts[times[-1] - offset + preset : len(timemidpts)] = (books[-1]['ask'][0,0] + books[-1]['bid'][0,0]) / 2.0

    return timemidpts

def getDifferenceArray(timemidpts, interval):

    # PD = avg midpt over (t,t+k) - avg midpt over (0,t)

    pd = np.zeros(len(timemidpts) - 2 * interval - 1)
    #av = np.zeros(len(pd) + 1)

    #for i in xrange(0, len(pd)):
    #    av[i] = np.mean(timemidpts[i: i - 1 + interval])

    #pd = np.diff(av)


    pd[0] = sum(timemidpts[interval:2*interval - 1]) - sum(timemidpts[0:interval-1])

    for i in xrange(1, len(pd)):
    # cheesy cheat, not sure if actually saves time?
    # task: reimplement with just adding arrays 
        pd[i] = pd[i-1] + timemidpts[i-1] - 2*timemidpts[i+interval-1] + timemidpts[i+2*interval-1]


    # Take the average
    pd = pd / interval;

    return pd

###########
# MAIN
###########


if __name__ == "__main__":
    print "Computing Regressions"

    # Set Parameters

    yr = sys.argv[1]

    dates = glob.glob(DATA_FOLDER + yr + '*')

    interval = 1 # in milliseconds
    stock_list = ['XHB' , 'NYX' , 'XLK' , 'IBM' , 'CVX' , 'VHT' , 'AAPL' , 'DIA' , 'VDC' , 'BP' , 'BAC' , 'XLY' , 'XLV' , 'MSFT' , 'XLP' , 'VPU' , 'SPY' , 'PG' , 'VNQ' , 'XLF' , 'CME' , 'HD' , 'GOOG' , 'C' , 'GS' , 'XLE' , 'XLB' , 'GE' , 'VGT' , 'JPM' , 'XOM' , 'VAW' , 'PFE' , 'CSCO' , 'VCR' , 'VIS' , 'QQQ' , 'MS' , 'JNJ' , 'VOX' , 'LOW' ]

    # For each stock, we need to do the following
    products = stock_list #['AAPL', 'XOM', 'GE', 'JNJ', 'IBM', 'DIA']
    #products = ['AAPL','GOOG']

    for date in dates:
        valid_products = []

        print "Processing ", date
        datestr = date[38:46]

        filename = datestr + "_TOP.h5" # "20111017_TOP.h5"

        start = time.time()

        # Load file
        input_file = tables.openFile(DATA_FOLDER + filename)

        loaddone = time.time()
        #print "load time:\t", loaddone - start

        # Get list of all stocks in data file
        # for now, we know all the stocks so we will just set it manually
    
        ## Filter for stock

        START_TIME = dt.time(8, 30, 00, 0) # 1430 GMT = 9:30AM Eastern
        END_TIME = dt.time(14, 00, 00, 0) # 2000 GMT = 3:00PM Eastern
    
        for i in xrange(len(products)):
            try:
                product = products[i]

                temp = filterData(input_file, product, START_TIME, END_TIME, datestr)

                filterdone = time.time()
                #if i == 0:
                #    print "filter time:\t", filterdone - loaddone
                #else:
                #    print "filter time:\t", filterdone - diffdone

                # break up temp
                books = temp[0]
                init = temp[1]
                end = temp[2]

                timemidpts = toTimeSpace(books, START_TIME, END_TIME, init, end)

                timespacedone = time.time()
                #print "tspace time:\t", timespacedone - filterdone
                
                try:
                    pd[i,:] = getDifferenceArray(timemidpts, interval)
                except:
                    pd = np.zeros([len(products), len(timemidpts) - 2 * interval - 1])
                    pd[i,:] = getDifferenceArray(timemidpts, interval)            

                diffdone = time.time()
                #print "diff time:\t", diffdone - timespacedone
                valid_products.append(product)
            except:
                print products[i], 'failed'


        

        # Take correlation across stocks
        corr = np.corrcoef(pd)
        corrdone = time.time()
        #print "corr time:\t", corrdone - diffdone

        """
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
        """

        # Print calculated correlations to file
        outstr = ""
        for i in xrange(len(valid_products)):
            for j in xrange(len(valid_products)):
                outstr = outstr + valid_products[i] + "," + valid_products[j] + "," + "{0:.5f}".format(corr[i,j]) + "\n"

        f = open("corr" + "_" + str(interval) + "_" + datestr + "_" + ''.join(products) + ".csv", 'w')
        f.write(outstr)


        #np.savetxt("pd.csv", np.transpose(pd), delimiter=",")

        # Clean up
        input_file.close()
