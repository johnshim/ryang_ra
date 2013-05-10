import tables
from tables import *
import numpy

import datetime as dt

# VARS FOR TESTING
DATA_FOLDER = "/media/sf_Dropbox/Work/budish_ra/data/"
FILE = "20111017f"

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

def book2time(filename):

    # Open files
    sourcedata = tables.openFile(filename)

    times1000 = sourcedata.root.ES.books.cols.timestamp[:]
    times = times1000 / 1000
    print times[0], times[-1]

    books = sourcedata.root.ES.books

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

    output.createArray(output.root, "test", timemidpts)

    # Cleaning Up
    sourcedata.close()
    output.close()
    

if __name__ == "__main__":
    print "TESTING NAIVE BOOK TO TIME"


    book2time(DATA_FOLDER + FILE)
