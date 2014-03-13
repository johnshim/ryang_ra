import tables
from tables import *
import numpy

import datetime as dt

# VARS FOR TESTING
DATA_FOLDER = "/datastore/dbd/auction/book_data/arca/"
FILE = "20100507_TOP.h5"

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

def ordercount(filename):

    # Open files
    sourcedata = tables.openFile(filename)

    times1000 = sourcedata.root.SPY.books.cols.timestamp[:]
    times = times1000 / 1000
    print "init: \t", times[0], "\t end: \t", times[-1]
    print "tttime: \t", times[-1] - times[0]
    print "len: \t",len(times1000)

    init = 0

    initt = times[0]

    one_sec = 1000; # 1 sec = 1000 ms
    n_updates = 0

    for i in xrange(len(times1000)):
        # if we need to update our range
        if times1000[i] > initt + one_sec:
            n_updates = n_updates + 1
            while initt < times1000[i] - one_sec:
                init = init + 1
                initt = times1000[init]
                n_updates = n_updates - 1
        else: # if this book update still in this second
            n_updates = n_updates + 1

    print "MAX UPDATES IN 1 SEC: ", n_updates

    # Cleaning Up
    sourcedata.close()
    

if __name__ == "__main__":
    print "TESTING NAIVE BOOK TO TIME"
    print "...",
    ordercount(DATA_FOLDER + FILE)

    print "DONE"
