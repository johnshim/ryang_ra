# External packages

import tables

from tables import *

import datetime as dt
import time
import numpy
import numpy as np

# Ron's packages


# VARS
DATA_FOLDER = "/media/sf_Dropbox/Work/budish_ra/data/"
FILE = "20111017"

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

    print times[0], times[-1]


    print START_TIME, END_TIME
    print '%f' % (init / 1000), '%f' % (end / 1000)

    # total number of milliseconds
    total_interval = times[-1] - times[0]
    print total_interval
    total_interval = end - init
    print total_interval

    # Offset for times
    offset = times[0]

    preset = times[0] - init
    postset = end - times[-1]

    # Array
    # (i, 1) is midpt price at time offset + i
    # (i, 2) is timestamp at time offset + i
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

    pd = np.zeros(len(timemidpts) - 2 * interval - 1)
    pd[0] = sum(timemidpts[interval:2*interval - 1]) - sum(timemidpts[0:interval-1])

    for i in xrange(1, len(pd)):
        # cheesy cheat, not sure if actually saves time?
        # task: reimplement with just adding arrays
        pd[i] = pd[i-1] + timemidpts[i-1] - 2*timemidpts[i+interval-1] + timemidpts[i+2*interval-1]

    return pd

if __name__ == "__main__":
    print "Computing Regressions"

    datestr = '20111017'
    filename = datestr + "_TOP.h5" # "20111017_TOP.h5"

    # Load file
    input_file = tables.openFile(DATA_FOLDER + filename)

    # Get list of all stocks in data file
    # for now, we know all the stocks so we will just set it manually
    stock_list = ['XHB' , 'NYX' , 'XLK' , 'IBM' , 'CVX' , 'VHT' , 'AAPL' , 'DIA' , 'VDC' , 'BP' , 'BAC' , 'XLY' , 'XLV' , 'MSFT' , 'XLP' , 'VPU' , 'SPY' , 'parse_results' , 'PG' , 'VNQ' , 'XLF' , 'CME' , 'HD' , 'GOOG' , 'C' , 'GS' , 'XLE' , 'XLB' , 'GE' , 'VGT' , 'JPM' , 'XOM' , 'VAW' , 'PFE' , 'CSCO' , 'VCR' , 'VIS' , 'QQQ' , 'MS' , 'JNJ' , 'VOX' , 'LOW' ]


    # For each stock, we need to do the following

    product = 'GS'
    product2 = 'MS'
    
    ## Filter for stock

    START_TIME = dt.time(14, 30, 00, 0) # 1430 GMT = 9:30AM Eastern
    END_TIME = dt.time(20, 00, 00, 0) # 2000 GMT = 3:00PM Eastern
    
    interval = 100

    temp = filterData(input_file, product, START_TIME, END_TIME, datestr)

    books = temp[0]
    init = temp[1]
    end = temp[2]

    timemidpts = toTimeSpace(books, START_TIME, END_TIME, init, end)
    pd = np.zeros([2, len(timemidpts) - 2 * interval - 1])
    pd[0,:] = getDifferenceArray(timemidpts, interval)
    
    temp2 = filterData(input_file, product2, START_TIME, END_TIME, datestr)

    books2 = temp2[0]
    init = temp2[1]
    end = temp2[2]

    timemidpts2 = toTimeSpace(books2, START_TIME, END_TIME, init, end)
    pd[1,:] = getDifferenceArray(timemidpts2, interval)

    # Take correlation across stocks
    corr = np.corrcoef(pd)
    print corr

    np.savetxt("pd.csv", np.transpose(pd), delimiter=",")

    # Clean up
    input_file.close()
