# book_to_time.py
# Converts records in book update space to time space

import tables
import numpy
import datetime as dt

from tables import *
from time import sleep

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
    f = tables.openFile(DATA_FOLDER + FILE)
    f2 = tables.openFile(DATA_FOLDER + FILE + 'ts', mode = "w", title = "outfile")

    contract_name = "ES"
    books = f.root.ES.books
    trades = f.root.ES.trades

    inittime = books.cols.timestamp[0]
    endtime = books.cols.timestamp[-1]
    print inittime, endtime, endtime - inittime

    readCtr = 0
    curr = books[0]
    old = books[0]

    group = f2.createGroup("/", "ES", "ES")

    table = f2.createTable(group, "books", BookTable, "books books")
    snap = table.row

    for i in xrange(inittime, endtime+1000, 1000):
        
        #print i, curr['timestamp']

        if int(curr['timestamp']) == i:
            #print "match"

            # push curr to new table

            snap['ask'] = curr['ask']
            snap['bid'] = curr['ask']
            snap['timestamp'] = i
            snap['timestamp_s'] = curr['timestamp_s'] # placeholder
            snap['seqnum'] = curr['seqnum']
            snap.append()

            # Increment
            old = curr
            readCtr += 1
            try:
                curr = books[readCtr]
            except IndexError:
                print endtime, i
                if i == int(endtime):
                    break
                else:
                    print "problem"
                    break
        elif int(curr['timestamp']) > i:
            #print "no book update yet"
            
            # push old to new table
            snap['ask'] = old['ask']
            snap['bid'] = old['ask']
            snap['timestamp'] = i
            snap['timestamp_s'] = old['timestamp_s'] # placeholder
            snap['seqnum'] = old['seqnum']
            snap.append()


            continue
        elif int(curr['timestamp']) < i:
            #print "missed an update"

            # push curr to new table
            snap['ask'] = curr['ask']
            snap['bid'] = curr['ask']
            snap['timestamp'] = i
            snap['timestamp_s'] = curr['timestamp'] # placeholder
            snap['seqnum'] = curr['seqnum']
            snap.append()


            old = curr
            readCtr += 1
            curr = books[readCtr]

            #sleep(1)

    table.flush()

    f.close()
    f2.close()
