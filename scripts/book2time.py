# book2time.py
# Converts records in book update space to time space

from functools import partial

from naive_book_to_time import book2time

import tables
import numpy
import datetime as dt

import time

import csv

import multiprocessing as mp

from tables import *
from time import sleep

import sys

import numpy as np

# VARS
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




if __name__ == "__main__":
    #ti = TimeIndexFinder(DATA_FOLDER + FILE)
    #ti2 = TimeIndexFinder(DATA_FOLDER + FILE)
    """
    i = time.time()
    for x in xrange(100):
        ti.get_index(1318886012570000)
        ti.get_index(1318886012570000 + x * 1000)

    print time.time() - i

    i = time.time()

    for x in xrange(100):
        ti.get_index_original(1318886012570000)
        ti.get_index_original(1318886012570000 + x * 1000)

    print time.time() - i
    """

    t = time.time()

    # Opening files (for both read and write)

    f = tables.openFile(DATA_FOLDER + FILE)
    f2 = tables.openFile(DATA_FOLDER + FILE + 'prices', mode='w', title = 'prices')
    f3 = tables.openFile(DATA_FOLDER + FILE + 'pdiff', mode='w', title = 'prices')

    # Extract the order books from hdf5

    books = f.root.ES.books

    # Get start and stop times

    init = books.cols.timestamp[0]
    end = books.cols.timestamp[-1]

    # times is a list of all the individual milliseconds (the timestamps are in 1/1000 of ms)
    # uno is just the first quarter of the observations

    times = xrange(init, end, 1000)
    uno = xrange(init, init + (end - init)/4, 1000)
    uno = xrange(init, end, 1000)
    #dos = xrange(init + (end-init)/2, end, 1000)


    #####

    # NAIVE BOOK TO TIME

    #####

    m = book2time(DATA_FOLDER + FILE)

    

    #####


    # Calculate midpoint prices (so far just for first quarter)

    #m = get_midpts(ti, books, uno)

    print "reading done in ", (time.time() - t) / 60.
    t = time.time()

    # Write the midpoints to file

    f2.createArray(f2.root, "test", m)

    print "writing done in ", (time.time() - t) / 60.
    t = time.time()

    # Calculate difference of averages over given interval

    interval = 10

    pd = np.zeros(len(m) - 2 * interval - 1)
    pd[0] = sum(m[interval:2*interval - 1]) - sum(m[0:interval-1])

    for i in xrange(1, len(pd)):
        # cheesy cheat, not sure if actually saves time?
        pd[i] = pd[i-1] + m[i-1] - 2*m[i+interval-1] + m[i+2*interval-1]

    # Write averages to file

    f3.createArray(f3.root, "pdiff", pd)

    print "Calc'ing PD done in ", (time.time() - t) / 60.

    f.close()
    f2.close()
    f3.close()

    # DO WITH NUMPY ARRAY

    #print len(uno), len(dos), len(end - init)

    #ti.books = books

    #def gm(x):
    #    return get_midpts(ti, books, x)

    #p = mp.Pool(2)
    #p.apply_async(get_midpts, (ti, books, uno))
    #p.apply_async(get_midpts, (ti, books, dos))
    #get_midpts(ti, books, uno)
    #m = p.map(gm, [uno, dos])
    #total = m[0] + m[1]
    #print len(total)
    #print end - init
    print "done"
    sys.exit()

