# External packages

import tables

from tables import *

# Ron's packages

from naive_book_to_time import book2time
from book2time import getDifferenceArray
from filter_data import filter_time_contract
from filter_data import get_front_month

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




if __name__ == "__main__":
    print "Computing Regressions"

    datestr = '20111017'
    filename = datestr + "_TOP.h5" # "20111017_TOP.h5"

    # Load file
    input_file = tables.openFile(DATA_FOLDER + filename)

    # Get list of all stocks in data file
    # for now, we know all the stocks so we will just set it manually
    stock_list = ['XHB' , 'NYX' , 'XLK' , 'IBM' , 'CVX' , 'VHT' , 'AAPL' , 'DIA' , 'VDC' , 'BP' , 'BAC' , 'XLY' , 'XLV' , 'MSFT' , 'XLP' , 'VPU' , 'SPY' , 'parse_results' , 'PG' , 'VNQ' , 'XLF' , 'CME' , 'HD' , 'GOOG' , 'C' , 'GS' , 'XLE' , 'XLB' , 'GE' , 'VGT' , 'JPM' , 'XOM' , 'VAW' , 'PFE' , 'CSCO' , 'VCR' , 'VIS' , 'QQQ' , 'MS' , 'JNJ' , 'VOX' , 'LOW' ]


    # For Day (We will start by writing this to calculate for a given day)

    # For each stock, we need to do the following

    product = stock_list[0]
    
    ## Filter for stock

    START_TIME = dt.time(13, 59, 59, 999999) # 8:30am = 1430 GMT
    END_TIME = dt.time(20, 00, 00, 1) # 3pm = 2000 GMT
    #END_TIME = dt.time(19, 00, 05, 1) # 2pm = 1900 GMT = 1400 EST


    # Convert to time date
    date = dt.date(int(datestr[0:4]), int(datestr[4:6]), int(datestr[6:8]))
    
    # get the front month contract only 
    # (This doesn't matter because we're working w/ equities
    # contract_name = get_front_month(date, product)
    contract_name = product
    front_contract = getattr(input_file.root, contract_name)

    # Filter by time
    init = time.mktime(dt.datetime.combine(date, start_time).timetuple()) * 1000000
    end = time.mktime(dt.datetime.combine(date, end_time).timetuple()) * 1000000

    selected_books = front_contract.books.readWhere('(timestamp >= init) & (timestamp <= end)')

    # Difference Function
    #
    # getDifferenceArray(symbol, datestr)

        # Extract the relevant timestamps

    times1000 = selected_books['timestamp']
    times = times1000 / 1000
    print times[0], times[-1]

    books = selected_books

    # total number of milliseconds
    total_interval = times[-1] - times[0]
    print total_interval

    # Offset for times
    offset = times[0]

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
            timemidpts[t - offset] = (books[i]['ask'][0,0] + books[i]['bid'][0,0]) / 2.0

        # If gap in updates, we need to replicate old price
        elif t > oldUpdateTime:
            # Copy old time for diff times
            timemidpts[oldUpdateTime - offset : t - offset] = oldPrice

            # Update book at new time
            timemidpts[t - offset] = (books[i]['ask'][0,0] + books[i]['bid'][0,0]) / 2.0
        else:
            print "ERROR"

        # Update previous update time/price
        oldUpdateTime = t
        oldPrice = (books[i]['ask'][0,0] + books[i]['bid'][0,0]) / 2.0

    


    # Get differences of stock

    # set interval for now
    interval = 10

    pd = np.zeros(len(m) - 2 * interval - 1)
    pd[0] = sum(m[interval:2*interval - 1]) - sum(m[0:interval-1])

    for i in xrange(1, len(pd)):
        # cheesy cheat, not sure if actually saves time?
        # task: reimplement with just adding arrays
        pd[i] = pd[i-1] + m[i-1] - 2*m[i+interval-1] + m[i+2*interval-1]

    # Take correlation across stocks
    

    # Clean up
    raw_data.close()
